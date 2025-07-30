# -*- coding: utf-8 -*-
# 2018 to present - Copyright Microchip Technology Inc. and its subsidiaries.

# Subject to your compliance with these terms, you may use Microchip software
# and any derivatives exclusively with Microchip products. It is your
# responsibility to comply with third party license terms applicable to your
# use of third party software (including open source software) that may
# accompany Microchip software.

# THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
# EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
# WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR
# PURPOSE. IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL,
# PUNITIVE, INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY
# KIND WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP
# HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
# FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
# ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
# THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.

import os
import shutil
import zipfile
import cryptoauthlib as cal
from tpds.secure_element import ECC608A
from tmng_manifest_lite import TMNGTLSManifestLite

folder = None

class TMNGManifest:
    global folder
    def __init__(self):
        pass

    def generate_manifest(self, file=""):
        """
        Method encode the trustflex manifest data and generate
        securesigned element by signing manifest data and
        store it in manifest file

        Args:
            file (str): manifest JSON filename
        """

        if not file:
            file = 'TMNGTLS_device_manifest.json'

        manifest_ca_key = "manifest_ca.key"
        manifest_ca_cert = "manifest_ca.crt"

        manifest = TMNGTLSManifestLite()
        manifest.load_manifest_uniqueid()
        if os.path.exists(manifest_ca_cert) and os.path.exists(manifest_ca_key):
            signed_se = manifest.encode_manifest(manifest_ca_key, manifest_ca_cert)
        else:
            signed_se = manifest.encode_manifest()
        self.signed_se = signed_se.get("signed_se")
        manifest.write_signed_se_into_file(self.signed_se, file)
        new_dir = folder
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        files_to_move = [manifest_ca_key,manifest_ca_cert,file]
        for file_name in files_to_move:
            shutil.move(file_name, os.path.join(new_dir, file_name))
        json_files = [file for file in os.listdir(new_dir) if file.endswith('.json')]
        zip_file_path = os.path.join(new_dir, f'mfst_{serial_number.hex()}.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file in json_files:
                file_path = os.path.join(new_dir, file)
                zipf.write(file_path,file)
        print(folder)

    def read_manifest(self):
        manifest = TMNGTLSManifestLite()
        se = manifest.decode_manifest(self.signed_se, ca_cert=f'{folder}\manifest_ca.crt')


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == "__main__":
    res = TMNGManifest()
    element = ECC608A(address=0x70)
    serial_number = bytearray()
    assert cal.atcab_read_serial_number(serial_number) == cal.Status.ATCA_SUCCESS, 'Error reading Serial Number'
    folder = "mfst_"+serial_number.hex()
    manifest = res.generate_manifest(file=f'mfst_{serial_number.hex()}.json')
    res.read_manifest()
    pass
