# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
import yaml
import struct
from intelhex import IntelHex
from pathlib import Path
from cryptography.hazmat.primitives import hashes, asymmetric
import cryptoauthlib as cal
from tpds.settings import TrustPlatformSettings
from tpds.helper import UsecaseLogger
from tpds.flash_program import FlashProgram
from tpds.api.api.hw.api_board import get_details
from ...api.models import UsecaseResponseModel
from ..proto_provision.helper.helper import check_board_status
from ..proto_provision.helper.keys import get_public_key_from_file_bytes, get_public_pem
from ..proto_provision.connect import Connect
from ...key_stream import KeyStream


class FoTA(Connect):
    def __init__(self, usecase_dir: str = None) -> None:
        self.usecase_dir = usecase_dir if usecase_dir else \
            os.path.join(TrustPlatformSettings().get_base_folder(), "keystream_fota")
        os.makedirs(self.usecase_dir, exist_ok=True)
        self.key_stream = None
        self.logger = UsecaseLogger(self.usecase_dir)
        self.key_name = None
        self.pub_uid, self.keystream_auth_token = None, None
        self.comp_1, self.comp_2 = None, None
        self.comp_1_info_addr, self.comp_2_info_addr = None, None
        self.comp_combined_file = None
        self.ssid, self.password = None, None
        self.signer_pub_key, self.public_key = None, None
        self.ks_creds_file = os.path.join(TrustPlatformSettings().get_base_folder(), 'keystream_config.yaml')
        self.file_creds = {
            "title": "Wifi credentials, Public Profile UID and keySTREAM Authentication token."
        }
        # List of (attribute name, error message) pairs
        self.credentials = [
            ("pub_uid", "Please Provide Fleet Profile Public UID Backup Not Available"),
            ("keystream_auth_token", "Please Provide keySTREAM Authorization Token Backup Not Available"),
            ("key_name", "Please Provide keySTREAM Signing Key Name Backup Not Available"),
            ("ssid", "Please Provide WIFI SSID Backup Not Available"),
            ("password", "Please Provide WiFi Password Backup Not Available"),
        ]

    def generate_resources(self, user_inputs: dict) -> UsecaseResponseModel:
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            self.logger.log("Generating Resources....")
            self.parse_user_inputs(user_inputs)
            self.logger.log("Connecting to KeySTREAM....")
            self.key_stream = KeyStream(self.keystream_auth_token, self.pub_uid)
            self.logger.log("Connected")
            self.logger.log("Fetching Signer Public Key")
            pub_responese = self.key_stream.get_trusted_pub_key(self.key_name)
            self.signer_pub_key = pub_responese.get("rawPublicKey")
            self.public_key = get_public_key_from_file_bytes(pub_responese.get("asn1PublicKey"))
            get_public_pem(self.public_key, f"{self.key_name}.pem")
            self.logger.log(f"Signer Public Key saved in : {self.key_name}.pem")
            self.fw_resources()
            combined_ih = IntelHex()
            for component, info_addr in [
                (self.comp_1, self.comp_1_info_addr),
                (self.comp_2, self.comp_2_info_addr),
            ]:
                if component:
                    Path("temp.hex").write_bytes(bytes.fromhex(component))
                    ih_comp = IntelHex(source="temp.hex")
                    ih_comp.padding = 0xFF
                    _, version, _, addr, size, sign_addr = struct.unpack("<IIIIII", ih_comp.gets(info_addr, 24))
                    file = f"component_{version.to_bytes(4, 'little').hex().upper()}"
                    data = bytes(ih_comp.tobinarray(addr, size=size))
                    comp_digest = self.key_stream.caluclate_digest(data)
                    self.logger.log(f"Component Digest: {comp_digest.hex().upper()}")
                    signature_resp = self.key_stream.sign(self.key_name, comp_digest)
                    signature = signature_resp.get("rawSignature")
                    self.logger.log(f"Component Signature: {signature.hex().upper()}")
                    self.logger.log("Verifying signature......")
                    self.verify_signature(data, signature_resp.get("asn1Signature"))
                    self.logger.log("Verification is successful!")
                    ih_comp[sign_addr: sign_addr + len(signature)] = list(signature)
                    ih_comp.write_hex_file(f"{file}.hex", byte_count=32)
                    ih_comp.tobinfile(f"{file}.bin")
                    self.logger.log(f"Component saved as {file} hex and bin")
                    combined_ih.merge(ih_comp, overlap='replace')

            # If both components are provided, create combined file including BANK2
            self.comp_combined_file = None
            if self.comp_1 and self.comp_2:
                self.logger.log(f"Generating Combined Component")
                self.comp_combined_file = "combined_component.hex"
                combined_ih.frombytes(bytes=bytes(combined_ih.tobinarray()), offset=0x00080000)
                combined_ih.write_hex_file(self.comp_combined_file, byte_count=32)
                combined_ih.tobinfile(self.comp_combined_file.replace("hex", "bin"))

            response.status = True
            response.message = "Resource generation is successful"
        except Exception as e:
            response.message = f"Resource generation has failed with: {e}"
        finally:
            os.remove("temp.hex") if os.path.exists("temp.hex") else None
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def proto_provision(self, user_inputs: dict) -> UsecaseResponseModel:
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            self.logger.log("Provisioning resources...")
            check_board_status(user_inputs.get("selectedBoard", None), self.logger)
            super().__init__(interface="I2C", address="0x70", devtype=cal.ATCADeviceType.ATECC608)
            self.logger.log("Loading Signer Public Key into Slot 15....")
            status = cal.atcab_write_pubkey(15, self.signer_pub_key)
            assert cal.Status.ATCA_SUCCESS == status, f"Write Signer Public Key failed with status {status:02X}"
            if self.comp_combined_file and os.path.exists(comp_combined_file := os.path.abspath(self.comp_combined_file)):
                self.logger.log(f"Loading Combined Component File: {comp_combined_file} into device....")
                self.load_image(comp_combined_file, user_inputs.get("selectedBoard"))
            response.status = True
            response.message = "Proto provision is successful"
        except Exception as e:
            response.message = f"Proto provision has failed with : {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def fw_resources(self) -> None:
        """
        Generates header file required for firmware project.
        """
        with open("fota_app_config.h", "w") as f:
            f.write("\n#ifndef _FOTA_APP_CONFIG_H\n")
            f.write("\n#define _FOTA_APP_CONFIG_H\n")
            f.write("\n#ifdef __cplusplus\n")
            f.write('extern "C" {\n')
            f.write("#endif\n\n")
            f.write('/** @brief Wifi SSID for TrustManaged device */\n')
            f.write(f'#define WIFI_SSID\t\t"{self.ssid}"\n\n')
            f.write('/** @brief Wifi password for TrustManaged device */\n')
            f.write(f'#define WIFI_PWD\t\t"{repr(self.password)[1:-1]}"\n\n')
            f.write('/** @brief TrustManaged Device Public UID */\n')
            f.write(f'#define KEYSTREAM_DEVICE_PUBLIC_PROFILE_UID\t"{self.pub_uid}"\n\n')
            f.write("#ifdef __cplusplus\n}\n")
            f.write("#endif\n")
            f.write("\n#endif // _FOTA_APP_CONFIG_H\n")
        self.logger.log("Generated fota_app_config.h file")

    def parse_user_inputs(self, user_inputs: dict):
        self.get_ks_creds_from_file()
        for attr, error_msg in self.credentials:
            value = self.get_required_credential(attr, user_inputs, error_msg)
            setattr(self, attr, value)
            self.logger.log(f"{attr.upper()}: {value}")

        self.comp_1 = user_inputs.get("comp_1").get("value")
        self.comp_1_info_addr = user_inputs.get("comp_1_info")
        if self.comp_1:
            assert self.comp_1_info_addr, "Please Provide Info Address for Component 1"
            self.comp_1_info_addr = int(self.comp_1_info_addr, 16)

        self.comp_2 = user_inputs.get("comp_2", None).get("value")
        self.comp_2_info_addr = user_inputs.get("comp_2_info")
        if self.comp_2:
            assert self.comp_2_info_addr, "Please Provide Info Address for Component 2"
            self.comp_2_info_addr = int(self.comp_2_info_addr, 16)
        self.save_ks_creds_to_file()

    def get_ks_creds_from_file(self):
        if os.path.exists(self.ks_creds_file):
            try:
                self.file_creds = yaml.safe_load(Path(self.ks_creds_file).read_text(encoding="utf-8"))
            except Exception as e:
                self.logger.log(f"Failed to Load {self.ks_creds_file} with error {e}")

    def save_ks_creds_to_file(self):
        ks_yaml_str = yaml.safe_dump(self.file_creds, sort_keys=False)
        Path(self.ks_creds_file).write_text(ks_yaml_str, encoding="utf-8")

    def get_required_credential(self, key: str, user_inputs: dict, error_message: str):
        value = user_inputs.get(key)
        if value and value.strip():
            self.file_creds.update({key: value})
            return value
        value = self.file_creds.get(key)
        if value and value.strip():
            return value
        raise ValueError(error_message)

    def load_image(self, image, board):
        flash_firmware = FlashProgram(board, get_details(board))
        flash_firmware.check_board_status()
        self.logger.log(f'Programming {image} file...')
        flash_firmware.load_hex_image_with_ipe(image)
        self.logger.log("Programmed")

    def delete_file(self, file):
        os.remove(file)
        os.remove(file.replace("hex", "bin"))

    def verify_signature(self, data: bytes, signature: bytes):
        self.public_key.verify(
            signature=signature,
            data=data,
            signature_algorithm=asymmetric.ec.ECDSA(hashes.SHA256())
        )
