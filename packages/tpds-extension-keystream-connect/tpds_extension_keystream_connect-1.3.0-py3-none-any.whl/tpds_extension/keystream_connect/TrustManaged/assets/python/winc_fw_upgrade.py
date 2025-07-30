# -*- coding: utf-8 -*-
import os
import time
import select
import platform
import traceback
import subprocess

from pykitinfo import pykitinfo
from pydebuggerupgrade.backend import Backend as dbgBackend
from pymcuprog.backend import Backend as progBackend
from pymcuprog.backend import SessionConfig  as progSessionConfig
from pymcuprog.toolconnection import ToolUsbHidConnection as progToolUsbHidConnection

from tpds.flash_program import FlashProgram
from tpds.tp_utils.tp_print import print
from tpds.tp_utils.tp_client import tpdsAPI_get
from tpds.tp_utils.tp_settings import TPSettings
import tpds.tp_utils.tp_input_dialog as tp_userinput

# Setting up winc_fw_upgrade base path
tp_settings = TPSettings()
TARGET_WINC_DIR = os.path.join(tp_settings.get_base_folder(), 'winc_firmware_upgrade')
# nedbg firmware path
NEDBG_FIRM_PATH = os.path.join(TARGET_WINC_DIR, 'nedbg_fw-1.18.528.zip')
# nedbg firmware path
D21E18_SERIAL_BRIDGE_FIRM_PATH = os.path.join(TARGET_WINC_DIR, 'firmware', 'Tools', 'serial_bridge', 'winc_serial_bridge.hex')
# winc upgrade bat path
WINC_FW_UPDATE_PATH = os.path.join(TARGET_WINC_DIR, 'firmware', 'download_all.bat')

class WincFirmwareUpdater():
    """
    Class for upgrading WINC1500 firmware 
    """

    def __init__(self, boards, winc_tool_type='UART', winc_tgtchip='3A0', aardvark='0'):
        """
        Initialize the WincFirmwareUpdater object.

        Parameters:
            boards (object): Object containing information about prototyping boards.
            winc_tool_type (str): Type of WINC tool to use (default is 'UART').
            winc_tgtchip (str): Target chip for WINC (default is '3A0').
            aardvark (str): Aardvark serial number (default is '0').
        """        
        # Boards details from notebook
        self.boards = boards
        # List to hold supported kit info
        self.WINC_UPGRADE_SUPPORTED_KITS = ['DM320118', 'EV10E69A']
        # Winc param details
        self.WINC_TOOL_TYPE = winc_tool_type
        self.WINC_TGTCHIP = winc_tgtchip
        self.AARDVARK_SNO = aardvark
        # Flash program instance
        self.flash_program = None
        # Board part num
        self.board_part_num = None
        # Kit name
        self.kit_name = None
        # MCU part num
        self.mcu_part_num = None
        # Kit COM port
        self.kit_com_port = None
        # Kit serial num
        self.kit_serial_num = None
        # Instantiate pydebuggerupgrade backend
        self.dbg_backend = dbgBackend()
        # Instantiate pymcuprog backend
        self.prog_backend = progBackend()        

    def set_board_name(self):
        """
        Set the board name based on the selected board.
        """        
        # Set Board part num
        self.board_part_num = self.boards.get_selected_board().get('name')
        return None

    def set_kit_name(self):
        """
        Retrieve and set information about the kit (kit name).
        """        
        # Set kit name
        self.board_info = tpdsAPI_get(f"boards/get_details/{self.board_part_num}")
        self.kit_name = self.board_info.kit_name
        return None

    def set_mcu_part_num(self):
        """
        Retrieve and set information about the kit (MCU part number).
        """                
        # Set kit name
        self.board_info = tpdsAPI_get(f"boards/get_details/{self.board_part_num}")
        self.mcu_part_num = self.board_info.mcu_part_number
        return None

    def check_board_selection(self):
        """
        Check if a prototyping board is selected.
        """
        if self.boards is None:
            print('Prototyping board MUST be selected!', canvas=b)
            return
        assert self.boards.get_selected_board(), \
            'Select board before running Winc Firmware update'
        
    def check_board_support(self):
        """
        Make sure selected board is supported for FW upgrade
        """
        if not (self.board_part_num in self.WINC_UPGRADE_SUPPORTED_KITS):
            raise Exception('Unsupported board for WINC Firmware upgrade')
        return None

    def check_board_connection(self):
        """
        Make sure selected board is connected to PC
        """        
        self.flash_program = FlashProgram(board_name=self.board_part_num)
        assert self.flash_program.is_board_connected(), \
            'Check the board connection'        
        return None

    def force_os_req(self):
        """
        Ensure the script only runs on Windows OS.
        """      
        if os.name != 'nt':  # 'nt' represents Windows OS
            raise OSError("This script can only run on Windows OS.")
        pathstr = os.environ.get('PATH')
        pathstr += ';C:\\windows\\system32;C:\\windows;'
        os.environ['PATH'] = pathstr  
        return None

    def raise_time_warning(self):
        """
        Create a message box to let user know about time taken for FW upgrade
        """
        status = None
        msg_box_info = f'<font color=#0000ff><b>Utility to upgrade WINC1500 firmware.<br> Click "OK" to upgrade firmware.<br><font color="green">This action can take upto 15mins.<br>Please wait until you see a status pop-up.</font></b></font><br>'
        modify_input_diag = tp_userinput.TPMessageBox(
            title="Winc1500 firmware upgrade",
            info=msg_box_info,
            option_list=['OK','Cancel'])
        modify_input_diag.invoke_dialog()
        if modify_input_diag.user_select == 'OK':
            status = 'ok'
        elif modify_input_diag.user_select == 'Cancel':
            raise Exception("User cancelled winc upgrade process")
        elif isinstance(e, TypeError):
            status = f"An unexpected error occurred: {e}"
            raise Exception("Please check the device connection.")
        return status
    
    def upgrade_success(self):
        """
        Create a message box to let user know that upgrade was successfull
        """
        msg_box_info = f'<font color=#0000ff><b>Winc1500 firmware upgrade success..</b></font><br>'
        modify_input_diag = tp_userinput.TPMessageBox(
            title="Winc1500 firmware update",
            info=msg_box_info,
            option_list=['OK'])
        modify_input_diag.invoke_dialog()

    def get_COM(self, kit_name):
        """
        Get the COM port associated with the specified kit name.

        Parameters:
            kit_name (str): Name of the kit.

        Returns:
            str : COM port number or None if not found.
        """        
        com_port = None
        kits = pykitinfo.detect_all_kits()
        for kit in kits:
            if kit_name== kit.get("debugger", {}).get("kitname", ""):
                port = kit.get("debugger", {}).get("serial_port", None)
                if port and platform.system() == "Windows":
                    com_port = int(port[3:])
                else:
                    com_port = port
        return com_port

    def get_kit_SN(self, kit_name):
        """
        Get the serial number of the kit with the specified name.

        Parameters:
            kit_name (str): Name of the kit.

        Returns:
            str or None: Serial number of the kit or None if not found.
        """        
        sno = None
        kits = pykitinfo.detect_all_kits()
        for kit in kits:
            if kit_name == kit.get("debugger", {}).get("kitname", ""):
                serial = kit.get("debugger", {}).get("serial_number", None)
                sno = serial
        return sno

    def program_debugger_firmware_by_kit_SN(self, kit_sn, firmware_hex_path):
        """
        Program the debugger firmware using the kit serial number.

        Parameters:
            kit_sn (str): Serial number of the kit.
            firmware_hex_path (str): Path to the debugger firmware HEX file.
        """        
        try:
            self.dbg_backend.upgrade_from_source(source=firmware_hex_path, serialnumber=kit_sn, force=True)
        except BaseException as e:
            print(traceback.format_exc())
            raise ValueError(
                f'Debugger firmware programming failed with {e}'
            )
        finally:
            # delay to allow for USB re-enumeration
            time.sleep(2)  
        return None

    def program_mcu_firmware(self, serialnum, mcu_part_num, hex_file_to_program):
        """
        Program the MCU firmware using the specified serial number and HEX file.

        Parameters:
            serialnum (str): Serial number of the kit.
            mcu_part_num (str): MCU part number.
            hex_file_to_program (str): Path to the HEX file to program.
        """        
        try:    
            # Connect to tool
            self.prog_backend.connect_to_tool(
            progToolUsbHidConnection(serialnumber=serialnum)
            )
            # Start session
            self.prog_backend.start_session(progSessionConfig(mcu_part_num))
            # Do an chip erase
            self.prog_backend.erase()
            self.prog_backend.write_hex_to_target(hex_file_to_program)
            if self.prog_backend.verify_hex(hex_file_to_program):
                programming_status = "success"
            else:
                programming_status = "Verify-Fail"
        except BaseException as e:
            programming_status = "Prog-Fail"
            raise ValueError(
                f"Programming failed with {e}, \
                    Please rerun or program manually!"
            )
        finally:
            return programming_status

    def run_command(self, command, p_cwd):
        """
        Run a command in the specified directory and stream its output through print.
        This is a blocking function.

        Parameters:
            command (list): List containing the command and its arguments.
            p_cwd (str): Path to the directory where the command should be run.

        Returns:
            int: Return code of the command.
        """        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=p_cwd, bufsize=1)

        while True:
            # Read a chunk of bytes from stdout
            output_chunk = process.stdout.read(1)
            if output_chunk:
                # Decode the chunk to string using UTF-8 encoding
                output_str = output_chunk.decode('utf-8', errors='ignore')
                # Print the decoded chunk without stripping whitespace
                print(output_str, end='', flush=True)
            elif process.poll() is not None:
                # If there's no more output and the process has terminated, break the loop
                break

        # Wait for the process to finish
        process.wait()
        # Return the process return code
        return process.returncode

    def upgrade_winc1500(self, b=None):
        """
        Perform the WINC1500 firmware upgrade process.

        """        
        self.force_os_req()
        self.set_board_name()
        self.set_kit_name()
        self.set_mcu_part_num()
        self.check_board_selection()
        self.check_board_support()
        self.check_board_connection()
        self.raise_time_warning()

        # Get com port
        self.kit_com_port = self.get_COM(self.kit_name)
        if self.kit_com_port is None:
            raise Exception("Unable to get serial port. Please check the kit connections")
        
        # Get com port
        self.kit_serial_num = self.get_kit_SN(self.kit_name)
        if self.kit_serial_num is None:
            raise Exception("Unable to get kit serial number. Please check the kit connections")

        # Program nedbg firmware
        print("Programming debugger firmware", end='')
        self.program_debugger_firmware_by_kit_SN(firmware_hex_path=NEDBG_FIRM_PATH, kit_sn=self.kit_serial_num)
        print(" - Done")
        
        print(D21E18_SERIAL_BRIDGE_FIRM_PATH)
        # Double check the hex, programming does not support the default elf
        if not os.path.exists(D21E18_SERIAL_BRIDGE_FIRM_PATH):
            raise ValueError("Missing Serial bridge firmware for ",self.mcu_part_num)
        
        # Program serial bridge firmware to D21E18
        print("Programming serial bridge firmware", end='')
        self.program_mcu_firmware(serialnum=self.kit_serial_num, mcu_part_num=self.mcu_part_num, hex_file_to_program=D21E18_SERIAL_BRIDGE_FIRM_PATH)
        print(" - Done")
        
        # delay to allow USB reenumeration
        time.sleep(2)  
        self.prog_backend.release_from_reset()
        # delay to allow USB reenumeration
        time.sleep(2)  
        self.prog_backend.end_session()       

        # Get abs dir path of the location containing the downloadall.bat file
        set_cwd = os.path.abspath(os.path.join(os.path.dirname(WINC_FW_UPDATE_PATH)))
        print(set_cwd)

        # Start winc upgrade
        bat_return_code = 9999
        print("Starting winc upgrade through serial port - {}".format(self.kit_com_port))
        try:
            command = [WINC_FW_UPDATE_PATH, self.WINC_TOOL_TYPE, self.WINC_TGTCHIP, self.AARDVARK_SNO, "{}".format(self.kit_com_port)]
            bat_return_code = self.run_command(command, p_cwd=set_cwd)
        except Exception as e:
            raise ValueError(
                f"Firmware upgrade failed with {e}"
            )            
        finally:    
            if bat_return_code==0:
                print("winc firmware upgrade success")
                self.upgrade_success()
                return None
            else:
                print("winc firmware upgrade fail")
                raise Exception("winc firmware upgrade fail, try again")
            