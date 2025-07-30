# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from enum import Enum
from cryptography.hazmat.primitives import hashes


class KeyAlgorithms(str, Enum):
    """Key Algorithms supported by the Secure Elements
    """
    ECC_P224 = "ECC_P224"
    ECC_P256 = "ECC_P256"
    ECC_P384 = "ECC_P384"
    ECC_P521 = "ECC_P521"
    RSA_1024 = "RSA_1024"
    RSA_2048 = "RSA_2048"
    RSA_3072 = "RSA_3072"
    RSA_4096 = "RSA_4096"
    HMAC_SHA256 = "HMAC_SHA256"
    ECC_SECP256_K1 = "ECC_SECP256K1"
    ECC_BRAINPOOL_P256_R1 = "ECC_Brainpool_P256R1"
    AES128 = "AES128"
    AES256 = "AES256"
    ED25519 = "Ed25519"
    X25519 = "X25519"


class KeySize(int, Enum):
    """KeySize class is an enumeration of the key sizes supported by the Secure Elements
    """
    ECC_P224 = 28
    ECC_P256 = 32
    ECC_P384 = 48
    RSA_1024 = 256
    RSA_2048 = 512
    RSA_3072 = 384
    HMAC_SHA256 = 32
    ECC_SECP256_K1 = 32
    ECC_BRAINPOOL_P256_R1 = 32
    AES128 = 16
    AES256 = 32
    ED25519 = 32


"""CurveKeyAlgoMap is a dictionary that maps the curve names/key size in bits
to the KeyAlgorithms
"""
CurveKeyAlgoMap = {
    "secp224r1": KeyAlgorithms.ECC_P224,
    "secp256r1": KeyAlgorithms.ECC_P256,
    "secp384r1": KeyAlgorithms.ECC_P384,
    "secp521r1": KeyAlgorithms.ECC_P521,
    "secp256k1": KeyAlgorithms.ECC_SECP256_K1,
    "brainpoolp256r1": KeyAlgorithms.ECC_BRAINPOOL_P256_R1,
    # RSA Keys don't have a curve name - just key size in bits
    1024: KeyAlgorithms.RSA_1024,
    2048: KeyAlgorithms.RSA_2048,
    3072: KeyAlgorithms.RSA_3072,
    4096: KeyAlgorithms.RSA_4096,
}

"""KeyHashAlgoMap is a dictionary that maps the KeyAlgorithms to the hash algorithms
"""
KeyHashAlgoMap = {
    KeyAlgorithms.ECC_P256: hashes.SHA256(),
    KeyAlgorithms.ECC_SECP256_K1: hashes.SHA256(),
    KeyAlgorithms.ECC_BRAINPOOL_P256_R1: hashes.SHA256(),
    KeyAlgorithms.ECC_P224: hashes.SHA224(),
    KeyAlgorithms.ECC_P384: hashes.SHA384(),
    KeyAlgorithms.ECC_P521: hashes.SHA512(),
    KeyAlgorithms.RSA_1024: hashes.SHA256(),
    KeyAlgorithms.RSA_2048: hashes.SHA256(),
    KeyAlgorithms.RSA_3072: hashes.SHA256(),
    KeyAlgorithms.RSA_4096: hashes.SHA256(),
    KeyAlgorithms.ED25519: None,
}
