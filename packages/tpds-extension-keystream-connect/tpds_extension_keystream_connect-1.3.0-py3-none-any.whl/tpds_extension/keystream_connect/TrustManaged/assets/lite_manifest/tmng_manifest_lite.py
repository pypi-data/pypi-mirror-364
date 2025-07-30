# -*- coding: utf-8 -*-
# 2015 to present - Copyright Microchip Technology Inc. and its subsidiaries.

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

import cryptoauthlib as cal

from tpds.manifest import Manifest


class TMNGTLSManifestLite(Manifest):
    """Class that sets required certificates, keys and unique ID to TFLXTLS devices

    Args:
        Manifest (object): base class
    """

    def __init__(self):
        super().__init__()
        self.model = "ATECC608"
        self.partNumber = "ATECC608-TMNGTLS"
        self.manufacturer = {
            "organizationName": "Microchip Technology Inc",
            "organizationalUnitName": "Secure Products Group",
        }
        self.provisioner = {
            "organizationName": "Microchip Technology Inc",
            "organizationalUnitName": "Secure Products Group",
        }
        self.distributor = {
            "organizationName": "Microchip Technology Inc",
            "organizationalUnitName": "Microchip Direct",
        }
        self.__dict__.pop('publicKeySet')

    def set_uniqueid(self):
        """Method sets an uniqueid to the device."""
        ser_num = bytearray(9)
        assert cal.atcab_read_serial_number(ser_num) == cal.Status.ATCA_SUCCESS
        super().set_unique_id(ser_num)

    def load_manifest_uniqueid(self):
        self.set_uniqueid()


__all__ = ["TMNGTLSManifestLite"]

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == "__main__":
    pass
