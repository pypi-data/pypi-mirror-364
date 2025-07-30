# -*- coding: utf-8 -*-
import os
import sys
import yaml
import requests
import tkinter as tk

from tkinter import messagebox
from contextlib import contextmanager

import tpds.tp_utils
import tpds.tp_utils.tp_input_dialog as tp_userinput
from tpds.tp_utils.tp_settings import TPSettings
from tpds.tp_utils.tp_print import print
from tpds.flash_program import FlashProgram


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


class keySTREAM_AWS_Cert_Mgmt():
    """
    A class to manage AWS certificates using keySTREAM.
    """

    def __init__(self, boards, ks_config_path, hfile_path):
        """
        Initialize the keySTREAM_AWS_Cert_Mgmt class.

        :param boards: The boards to be used.
        :param ks_config_path: Path to the keySTREAM configuration file.
        :param hfile_path: Path to the header file.
        """
        self.ks_config_path = ks_config_path
        self.hfile_path = hfile_path
        self.boards = boards

    def __connect_to_SE(self, b=None):
        """
        Connect to the Secure Element.

        :param b: Optional parameter.
        """
        print("Connecting to Secure Element: ")
        assert self.boards, "Prototyping board MUST be selected!"
        assert self.boards.get_selected_board(), "Select board to run an Usecase"

        kit_parser = FlashProgram()
        print(kit_parser.check_board_status())
        assert kit_parser.is_board_connected(), "Check the Kit parser board connections"
        factory_hex = self.boards.get_kit_hex()
        if not kit_parser.is_factory_programmed():
            assert factory_hex, "Factory hex is unavailable to program"
            print("Programming factory hex...")
            tp_settings = TPSettings()
            path = os.path.join(
                tp_settings.get_tpds_core_path(),
                "assets",
                "Factory_Program.X",
                factory_hex,
            )
            print(f"Programming {path} file")
            kit_parser.load_hex_image(path)
        print("OK")

    def manifest_lite(self, b=None):
        """
        Generate a lite manifest.

        :param b: Optional parameter.
        """
        try:
            self.__connect_to_SE()
            sys_shell = True if sys.platform == 'win32' else False
            lite_manifest_path = os.path.join(
                TPSettings().get_base_folder(),
                'keystream_connect', 'lite_manifest')

            os.chdir(lite_manifest_path)
            subProcessOut = tpds.tp_utils.run_subprocess_cmd(
                cmd=["python", "tmng_manifest_lite_generation.py"],
                sys_shell=sys_shell)
            if subProcessOut[0]:
                raise ValueError("Manifest_lite generation failed!\nPlease check the device connection.")
            else:
                zip_file_path = lite_manifest_path + "\\"
                zip_file_path_1 = subProcessOut[1].strip() + "\\" + subProcessOut[1].strip() + ".zip"
                msg_box_info = f'<font color=#0000ff><b>Manifest File generated in following path:</b></font><br>{zip_file_path}<br>{ zip_file_path_1}'
                modify_input_diag = tp_userinput.TPMessageBox(
                    title="Manifest_lite Generated Sucessfully",
                    info=msg_box_info,
                    option_list=['OK', 'Cancel'])
                modify_input_diag.invoke_dialog()

        except ValueError as e:
            raise e

    def get_inputs(self, b=None):
        """
        Get inputs from the user through a GUI.

        :param b: Optional parameter.
        """
        print('Executing Step-2..')
        # Create the main window
        root = tk.Tk()
        root.title("Edit Configuration")
        root.geometry("750x270")  # Set the size of the window
        root.attributes("-topmost", True)

        # Information label at the top of the form
        info_text = "Pre-config Input Selection:"
        info_label = tk.Label(root, text=info_text, font=("Arial", 11), justify="left", wraplength=400, fg="#0000ff")
        info_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        fields = ['Fleet Profile Public UID - Enter the Fleet Profile Public UID Created in keySTREAM UI',
                  'WiFi SSID - Provide WiFi SSID to which device needs to connect',
                  'WiFi Password - Provide Wifi Password for device to connect',
                  'keySTREAM Authorization Token (API Key) - Provide Authorization Token',
                  'AWS Access Key ID - Provide AWS Key ID',
                  'AWS Secret Access Key - Provide AWS Secret Access Key',
                  'Region - Provide AWS Region (eg:us-east-2)']
        entries = {}

        fields_mapping = {
            'Fleet Profile Public UID - Enter the Fleet Profile Public UID Created in keySTREAM UI': 'pub_uid',
            'WiFi SSID - Provide WiFi SSID to which device needs to connect': 'ssid',
            'WiFi Password - Provide Wifi Password for device to connect': 'password',
            'keySTREAM Authorization Token (API Key) - Provide Authorization Token': 'keystream_auth_token',
        }

        aws_mapping = {
            'AWS Access Key ID - Provide AWS Key ID': 'access_key_id',
            'AWS Secret Access Key - Provide AWS Secret Access Key': 'secret_access_key',
            'Region - Provide AWS Region (eg:us-east-2)': 'region'
        }

        ks_data = {}
        aws_cred_data = {}

        ks_creds_file = os.path.join(TPSettings().get_base_folder(), 'keystream_config.yaml')
        if os.path.exists(ks_creds_file):
            with open(ks_creds_file, 'r') as ks_file:
                ks_data = yaml.safe_load(ks_file) or {}
        else:
            print("Keystream Config File not found.")

        aws_creds_file = os.path.join(TPSettings().get_base_folder(), 'aws_credentials.yaml')
        if os.path.exists(aws_creds_file):
            with open(aws_creds_file, 'r') as aws_file:
                aws_cred_data = yaml.safe_load(aws_file) or {}
        else:
            print("AWS Credentials File not found.")

        # Processing keystream.yaml
        for index, field in enumerate(fields[:4]):
            label = tk.Label(root, text=field + ":", anchor="w")
            label.grid(row=index + 2, column=0, sticky="w", padx=10, pady=2)
            entry = tk.Entry(root, width=40)
            entry.grid(row=index + 2, column=1, sticky="e", padx=10, pady=2)
            mapped_key = fields_mapping.get(field)
            if mapped_key in ks_data:
                data_value = ks_data[mapped_key]
                if data_value is not None:
                    if data_value.startswith('Basic '):
                        data_value = data_value[6:]
                    entry.insert(0, data_value)
            entries[field] = entry

        # Processing aws_credentials.yaml
        for index, field in enumerate(fields[4:]):
            label = tk.Label(root, text=field + ":", anchor="w")
            label.grid(row=index + 6, column=0, sticky="w", padx=10, pady=2)  # Start from row 6
            entry = tk.Entry(root, width=40)
            entry.grid(row=index + 6, column=1, sticky="e", padx=10, pady=2)
            mapped_key = aws_mapping.get(field)
            if mapped_key in aws_cred_data:
                if aws_cred_data[mapped_key] is not None:
                    entry.insert(0, aws_cred_data[mapped_key])
            entries[field] = entry

        # Buttons for submitting or cancelling
        def submit_or_cancel(cancel=False):
            if cancel:
                root.destroy()
            else:
                data = {field: entries[field].get().strip() for field in entries}
                empty_fields = [field for field, value in data.items() if not value.strip()]
                if empty_fields:
                    messagebox.showwarning("Empty Fields", f"Please fill in the following fields: {', '.join(empty_fields)}")
                else:
                    data_keystream()
                    root.destroy()

        # Frame to contain the buttons
        button_frame = tk.Frame(root)
        button_frame.grid(row=len(fields) + 3, column=1, padx=0, pady=9, sticky="e")

        # Buttons within the frame
        ok_button = tk.Button(button_frame, text="Submit", command=lambda: submit_or_cancel(), font=("Arial", 9), width=12)
        ok_button.pack(side="left", padx=(0, 5))

        cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: submit_or_cancel(cancel=True), font=("Arial", 9), width=12)
        cancel_button.pack(side="left")

        def data_keystream():
            """
            Save the input data to the keystream and AWS credentials files.
            """
            ks_creds_file = os.path.join(TPSettings().get_base_folder(), 'keystream_config.yaml')
            aws_creds_file = os.path.join(TPSettings().get_base_folder(), 'aws_credentials.yaml')

            try:
                with open(ks_creds_file, 'r') as ks_file:
                    ks_data = yaml.safe_load(ks_file)
            except FileNotFoundError:
                ks_data = {}

            try:
                with open(aws_creds_file, 'r') as aws_file:
                    aws_cred_data = yaml.safe_load(aws_file)
            except FileNotFoundError:
                aws_cred_data = {}

            # Update the loaded data with new data
            data = {field: entries[field].get().strip() for field in entries}
            ks_data['pub_uid'] = data.get('Fleet Profile Public UID - Enter the Fleet Profile Public UID Created in keySTREAM UI')
            ks_data['ssid'] = data.get('WiFi SSID - Provide WiFi SSID to which device needs to connect')
            ks_data['password'] = data.get('WiFi Password - Provide Wifi Password for device to connect')
            token = data.get('keySTREAM Authorization Token (API Key) - Provide Authorization Token')
            ks_token = 'Basic ' + token
            ks_data['keystream_auth_token'] = ks_token
            aws_cred_data['access_key_id'] = data.get('AWS Access Key ID - Provide AWS Key ID')
            aws_cred_data['secret_access_key'] = data.get('AWS Secret Access Key - Provide AWS Secret Access Key')
            aws_cred_data['region'] = data.get('Region - Provide AWS Region (eg:us-east-2)')

            # Write updated data back into YAML files
            with open(ks_creds_file, 'w') as ks_file:
                yaml.dump(ks_data, ks_file, sort_keys=False)

            with open(aws_creds_file, 'w') as aws_file:
                yaml.dump(aws_cred_data, aws_file, sort_keys=False)

        root.mainloop()

    def get_cacert(self, b=None):
        """
        Execute Step-3: Download the CA certificate from keySTREAM and configure AWS credentials.

        This function performs the following steps:
        1. Reads the keySTREAM and AWS credentials from their respective YAML files.
        2. Sets the AWS credentials using the AWS CLI.
        3. Retrieves the AWS IoT endpoint.
        4. Writes the configuration to a header file.
        5. Retrieves the device manager UUID (dmuid) using the public UID.
        6. Retrieves the operational CA name.
        7. Downloads the CA certificate and saves it to a file.

        :param b: Optional parameter.
        :raises Exception: If any of the subprocess commands fail or if the CA certificate download fails.
        """
        print('Executing Step-3...')
        creds_file = os.path.join(self.ks_config_path, 'keystream_config.yaml')

        with open(creds_file) as f:
            data = yaml.safe_load(f)

        aws_creds_file = os.path.join(self.ks_config_path, 'aws_credentials.yaml')

        with open(aws_creds_file) as aws_file:
            aws_data = yaml.safe_load(aws_file)

        global headers
        headers = {
            'accept': 'application/json',
            'x-correlation-id': 'ISEPDMUI-4d1cff76-7ace-4fda-0811-488fb8d99cbf',
            'Authorization': data['keystream_auth_token']
        }

        ssid = data['ssid']
        password = data['password']
        pub_uid = data['pub_uid']
        global keystream_coap_endpoint
        global keystream_http_endpoint
        global keystream_endpoint

        keystream_coap_endpoint = data['keystream_coap_endpoint']
        keystream_http_endpoint = data['keystream_http_endpoint']
        # Only coap url could be accessed from outside via Rest API
        keystream_endpoint = data['keystream_coap_endpoint']
        # Setting AWS Credentials
        sys_shell = True if sys.platform == 'win32' else False
        subProcessOut = tpds.tp_utils.run_subprocess_cmd(
            cmd=[
                "aws", "configure", "set",
                "default.aws_access_key_id", aws_data['access_key_id']],
            sys_shell=sys_shell)

        if subProcessOut[0] != 0:
            raise Exception(f'Setting AWS Access key ID Failed!!!\nError:{subProcessOut[2]}.\n')

        subProcessOut = tpds.tp_utils.run_subprocess_cmd(
            cmd=[
                "aws", "configure", "set",
                "default.aws_secret_access_key", aws_data['secret_access_key']],
            sys_shell=sys_shell)

        if subProcessOut[0] != 0:
            raise Exception(f'Setting AWS Secret Access Key Failed!!!\nError:{subProcessOut[2]}.\n')

        subProcessOut = tpds.tp_utils.run_subprocess_cmd(
            cmd=[
                "aws", "configure", "set",
                "default.region", aws_data['region']],
            sys_shell=sys_shell)

        if subProcessOut[0] != 0:
            raise Exception(f'Setting AWS Region Failed!!!\nError:{subProcessOut[2]}.\n')

        # Getting AWS Endpoint
        subProcessOut = tpds.tp_utils.run_subprocess_cmd(
            cmd=[
                "aws", "iot", "describe-endpoint",
                "--endpoint-type", "iot:Data-ATS", "--output=text"],
            sys_shell=sys_shell)

        if subProcessOut[0] != 0:
            raise Exception(f'Getting AWS Endpoint Failed!!!\nError:{subProcessOut[2]}.\n')

        global aws_endpoint
        aws_endpoint = subProcessOut[1]
        aws_endpoint = aws_endpoint.replace('\n', '')
        # Writing config to header file
        ks_coap_url = "icpp." + keystream_coap_endpoint
        ks_http_url = "icph." + keystream_http_endpoint
        hfile_path = os.path.join(self.hfile_path, 'tmg_conf.h')
        with open(hfile_path, 'w') as fh:
            fh.write('/******************************************************************************\n')
            fh.write('*************************keySTREAM Trusted Agent ("KTA")***********************\n')
            fh.write('* (c) 2023-2024 Nagravision Sarl\n')
            fh.write('\n')
            fh.write('* Subject to your compliance with these terms, you may use the Nagravision Sarl\n')
            fh.write('* Software and any derivatives exclusively with Nagravision’s products. It is your\n')
            fh.write('* responsibility to comply with third party license terms applicable to your\n') 
            fh.write('* use of third party software (including open source software) that may accompany\n') 
            fh.write('* Nagravision Software.\n')
            fh.write('\n')
            fh.write('* Redistribution of this Nagravision Software in source or binary form is allowed\n') 
            fh.write('* and must include the above terms of use and the following disclaimer with the\n') 
            fh.write('* distribution and accompanying materials.\n')
            fh.write('\n')
            fh.write('* THIS SOFTWARE IS SUPPLIED BY NAGRAVISION "AS IS". NO WARRANTIES, WHETHER EXPRESS,\n') 
            fh.write('* IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED WARRANTIES OF\n') 
            fh.write('* NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE. IN NO\n') 
            fh.write('* EVENT WILL NAGRAVISION BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, INCIDENTAL\n') 
            fh.write('* OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND WHATSOEVER RELATED TO\n') 
            fh.write('* THE SOFTWARE, HOWEVER CAUSED, EVEN IF NAGRAVISION HAS BEEN ADVISED OF THE\n') 
            fh.write('* POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW,\n') 
            fh.write('* NAGRAVISION S TOTAL LIABILITY ON ALL CLAIMS IN ANY WAY RELATED TO THIS\n') 
            fh.write('* SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY\n') 
            fh.write('* TO NAGRAVISION FOR THIS SOFTWARE. \n')
            fh.write('******************************************************************************/\n')
            fh.write('/** \\brief  Configuration file for environment setup.\n')
            fh.write('*\n')
            fh.write('*  \\author Kudelski IoT\n')
            fh.write('*\n')
            fh.write('*  \date 2023/06/12\n')
            fh.write('*\n')
            fh.write('*  \\file tmg_conf.h\n')
            fh.write('******************************************************************************/\n\n')
            fh.write('/**\n')
            fh.write(' * @brief Configuration file for environment setup.\n')
            fh.write(' */\n\n')
            fh.write('#ifndef TMG_CONF_H\n')
            fh.write('#define TMG_CONF_H\n\n')
            fh.write('#ifdef __cplusplus\n')
            fh.write('extern "C" {\n')
            fh.write('#endif /* C++ */\n\n')
            fh.write('/* This header file generated from one of the TPDS steps */\n')
            fh.write('/* Please do NOT make any changes to this file */\n\n')
            fh.write('/* -------------------------------------------------------------------------- */\n')
            fh.write('/* IMPORTS                                                                    */\n')
            fh.write('/* -------------------------------------------------------------------------- */\n\n')
            fh.write('/* -------------------------------------------------------------------------- */\n')
            fh.write('/* CONSTANTS, TYPES, ENUM                                                     */\n')
            fh.write('/* -------------------------------------------------------------------------- */\n\n')
            fh.write('/** @brief Wifi SSID for TrustManaged device */\n')
            fh.write(f'#define WIFI_SSID                           "{ssid}"\n\n')
            fh.write('/** @brief Wifi password for TrustManaged device */\n')
            fh.write(f'#define WIFI_PWD                            "{repr(password)[1:-1]}"\n\n')
            fh.write('/** @brief TrustManaged Device Public UID */\n')
            fh.write(f'#define KEYSTREAM_DEVICE_PUBLIC_PROFILE_UID "{pub_uid}"\n\n')
            fh.write('/** @brief keySTREAM COAP Endpoint */\n')
            fh.write(f'#define KEYSTREAM_COAP_URL                  (const uint8_t*)"{ks_coap_url}"\n\n')
            fh.write('/** @brief keySTREAM HTTP Endpoint */\n')
            fh.write(f'#define KEYSTREAM_HTTP_URL                  (const uint8_t*)"{ks_http_url}"\n\n')
            fh.write('/** @brief AWS Endpoint */\n')
            fh.write(f'#define AWS_ENDPOINT                        "{aws_endpoint}"\n\n')
            fh.write('/* -------------------------------------------------------------------------- */\n')
            fh.write('/* VARIABLES                                                                  */\n')
            fh.write('/* -------------------------------------------------------------------------- */\n\n')
            fh.write('/* -------------------------------------------------------------------------- */\n')
            fh.write('/* FUNCTIONS                                                                  */\n')
            fh.write('/* -------------------------------------------------------------------------- */\n\n')
            fh.write('#ifdef __cplusplus\n')
            fh.write('}\n')
            fh.write('#endif /* C++ */\n\n')
            fh.write('#endif // TMG_CONF_H\n\n')
            fh.write('/* -------------------------------------------------------------------------- */\n')
            fh.write('/* END OF FILE                                                                */\n')
            fh.write('/* -------------------------------------------------------------------------- */\n')

        fh.close()
        #Getting the dmuid from public profile uid
        keystream_endpoint = "https://" + keystream_endpoint
        url = f"{keystream_endpoint}/dm?dpPublicUid={pub_uid}"
        response = requests.get(url, headers=headers)
        dm = response.json()
        if 'totalRecords' in dm and dm['totalRecords'] == 0:
            raise Exception('Invalid public Profile UID!!!\n Please Provide Valid Device Fleet Profile Public UID in Step-2\n')
        if response.status_code != 200:
            check_inputs = ['Device Public UID', 'KeySTREAM Authorization Token (API Key) and its Validity']
            if bool(check_inputs):
                check_inputs = '\n'.join(check_inputs)
                raise Exception(f'Request Failed!!!\nPlease check the following input parameters and retry:\n{check_inputs}.\n')
        
        dm = response.json()

        global dmuid
        dmuid = dm['deviceManagers'][0]['uuid']

        #Getting the Operational CA Name
        url = f"{keystream_endpoint}/dm/{dmuid}/business/deviceprofiles/desired?publicUid={pub_uid}&fields=zerotouch"

        response = requests.get(url, headers=headers)
        ca = response.json()
        global ca_name
        ca_name = ca['desiredProperties'][0]['zerotouch']['certificateAuthorityName']

        #Downloading CA Certificate
        print('Downloading CA Cert.....')
        url = f"{keystream_endpoint}/cm/dm/{dmuid}/certificateauthorities/{ca_name}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception('Downloading CA Cert Failed, Please provide valid input paramters in step 2.\n')
        ca_cert = response.json()
        print(ca_cert['certificate'])

        with open(f'{ca_name}_ca.pem', 'w') as f: 
            f.write("-----BEGIN CERTIFICATE-----\n")
            f.write(ca_cert['certificate'])
            f.write("\n-----END CERTIFICATE-----\n")

        print('Downloading CA certificate Done')
        
    def get_aws_code(self, b=None):
        """
        Execute Step-4: Retrieve the AWS registration code.

        This function performs the following steps:
        1. Executes the AWS CLI command to get the registration code.
        2. Prints the registration code.
        3. Stores the registration code in a global variable.

        :param b: Optional parameter.
        :raises Exception: If the subprocess command fails or if the registration code is None.
        """

        print('Executing Step-4...')

        sys_shell = True if sys.platform == 'win32' else False
        print("Getting AWS Registration Code")
        subProcessOut = tpds.tp_utils.run_subprocess_cmd(
            cmd=[
                "aws", "iot", "get-registration-code",
                "--region", "us-east-2","--output=text"],
            sys_shell=sys_shell)

        if subProcessOut[0] != 0:
            raise Exception(f'Getting AWS Registration code Failed!!!\nError:{subProcessOut[2]}.\n')

        print("Registration Code: ", subProcessOut[1])
        if subProcessOut[1] is None:
            raise Exception(subProcessOut[1])

        #AWS registration Code
        global reg_code
        reg_code = subProcessOut[1]

    
    def get_pop(self, b=None):
        """
        Execute Step-5: Download the Proof of Possession (PoP) certificate from keySTREAM.

        This function performs the following steps:
        1. Constructs the URL to download the PoP certificate.
        2. Sends a GET request to the URL.
        3. Saves the downloaded PoP certificate to a file.

        :param b: Optional parameter.
        :raises Exception: If the PoP certificate download fails.
        """        
        #Downloading Verification Certificate Certificate
        print('Executing Step-5...')

        print('Downloading PoP Cert from keySTREAM')

        url = f"{keystream_endpoint}/cm/dm/{dmuid}/certificateauthorities/{ca_name}/popcertificate/{reg_code}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception('Downloading PoP Cert Failed, Please provide valid input paramters in step 2.\n')
        pop_cert = response.json()
        print(pop_cert['popCertificate'])

        with open(f'{ca_name}_pop.pem', 'w') as f: 
            f.write(pop_cert['popCertificate'])

        print('Downloading PoP Certificate Done')


    def register_cert_to_aws(self, b=None):
        # Uploading Certificates to AWS
        print('Executing Step-6...')
        print("Uploading Signer Cert and Verification Cert To AWS")

        curr_path = os.getcwd()
        sys_shell = sys.platform == 'win32'  # True for Windows, False otherwise

        # Construct file paths
        ca_cert_path = os.path.join(curr_path, f"{ca_name}_ca.pem")
        verification_cert_path = os.path.join(curr_path, f"{ca_name}_pop.pem")

        # Construct AWS CLI command
        cmd = [
            "aws", "iot", "register-ca-certificate",
            "--ca-certificate", f"file://{ca_cert_path}",
            "--verification-cert", f"file://{verification_cert_path}",
            "--set-as-active", "--allow-auto-registration", "--region", "us-east-2"
        ]

        # Run the command
        subProcessOut = tpds.tp_utils.run_subprocess_cmd(cmd=cmd, sys_shell=sys_shell)

        # Handle output
        if "ResourceAlreadyExistsException" in subProcessOut[2]:
            print("Resource Already Exist!!!")
        elif subProcessOut[0] != 0:
            raise Exception(subProcessOut[2])       

        # Remove downloaded certificates
        os.remove(ca_cert_path)
        os.remove(verification_cert_path)