# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
import base64
from pathlib import Path
from typing import Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, ed25519, x25519
from cryptography.hazmat.primitives.asymmetric.types import (
    PRIVATE_KEY_TYPES, PUBLIC_KEY_TYPES)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    load_pem_private_key,
    load_pem_public_key,
    load_der_public_key,
    load_der_private_key
)
from ..helper.defines import KeyAlgorithms, CurveKeyAlgoMap


def generate_key_pair(key_type: KeyAlgorithms) -> PRIVATE_KEY_TYPES:
    """Generate the Key Pair based on the Key Type

    Args:
        key_type (KeyAlgorithms): Key Type to generate the Key Pair

    Returns:
        PRIVATE_KEY_TYPES: Private Key generated based on the Key Type
    """
    key_gen_api = {
        KeyAlgorithms.ECC_P224: ec.generate_private_key(ec.SECP224R1(), default_backend()),
        KeyAlgorithms.ECC_P256: ec.generate_private_key(ec.SECP256R1(), default_backend()),
        KeyAlgorithms.ECC_SECP256_K1: ec.generate_private_key(ec.SECP256K1(), default_backend()),
        KeyAlgorithms.ECC_BRAINPOOL_P256_R1: ec.generate_private_key(ec.BrainpoolP256R1(), default_backend()),
        KeyAlgorithms.ECC_P384: ec.generate_private_key(ec.SECP384R1(), default_backend()),
        KeyAlgorithms.ECC_P521: ec.generate_private_key(ec.SECP521R1(), default_backend()),
        KeyAlgorithms.ED25519: ed25519.Ed25519PrivateKey.generate(),
        KeyAlgorithms.X25519: x25519.X25519PrivateKey.generate(),
        KeyAlgorithms.RSA_1024: rsa.generate_private_key(public_exponent=65537, key_size=1024),
        KeyAlgorithms.RSA_2048: rsa.generate_private_key(public_exponent=65537, key_size=2048),
        KeyAlgorithms.RSA_3072: rsa.generate_private_key(public_exponent=65537, key_size=3072),
        KeyAlgorithms.RSA_4096: rsa.generate_private_key(public_exponent=65537, key_size=4096),
    }
    assert (private_key := key_gen_api.get(key_type, None)), \
        "Unknown Key type to process"
    return private_key


def get_public_key(private_key: PRIVATE_KEY_TYPES) -> PUBLIC_KEY_TYPES:
    """Get the Public Key from the Private Key

    Args:
        private_key (PRIVATE_KEY_TYPES): Private Key to get the Public Key

    Returns:
        PUBLIC_KEY_TYPES: Public Key generated from the Private Key
    """
    return private_key.public_key()


def get_public_key_bytes(public_key: PUBLIC_KEY_TYPES) -> bytes:
    """Get the Public Key Bytes from the Public Key

    Args:
        public_key (PUBLIC_KEY_TYPES): Public Key to get the Public Key Bytes

    Returns:
        bytes: Public Key Bytes from the Public Key
    """
    public_key_bytes = bytes()
    if isinstance(public_key, rsa.RSAPublicKey):
        public_key_bytes = public_key.public_numbers().n.to_bytes(
            int(public_key.key_size / 8), "big")
    elif isinstance(public_key, ed25519.Ed25519PublicKey) or isinstance(public_key, x25519.X25519PublicKey):
        public_key_bytes = public_key.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw)[1:]
    else:
        public_key_bytes = public_key.public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.UncompressedPoint)[1:]
    return public_key_bytes


def get_private_key_bytes(private_key: PRIVATE_KEY_TYPES) -> bytes:
    """Get the Private Key Bytes from the Private Key

    Args:
        private_key (PRIVATE_KEY_TYPES): Private Key to get the Private Key Bytes

    Returns:
        bytes: Private Key Bytes from the Private Key
    """
    private_key_bytes = None
    ecc_key_size = {
        "secp256r1": ec.SECP256R1.key_size,
        "secp224r1": ec.SECP224R1.key_size,
        "secp384r1": ec.SECP384R1.key_size,
        "secp521r1": 528,  # Setting fixed size of 66 bytes instead of 521 bits
        "secp256k1": ec.SECP256K1.key_size,
        "brainpoolP256r1": ec.BrainpoolP256R1.key_size,
    }
    if isinstance(private_key, rsa.RSAPrivateKey):
        private = private_key.private_numbers()
        private_key_p = bytearray(
            private.p.to_bytes(int((private_key.key_size / 8) / 2), "big")
        )
        private_key_q = bytearray(
            private.q.to_bytes(int((private_key.key_size / 8) / 2), "big")
        )
        private_key_bytes = private_key_p + private_key_q

    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        private_key_bytes = bytearray(
            private_key.private_numbers().private_value.to_bytes(
                int(ecc_key_size.get(private_key.curve.name) / 8), "big"
            )
        )
    elif isinstance(private_key, ed25519.Ed25519PrivateKey) or isinstance(private_key, x25519.X25519PrivateKey):
        private_key_bytes = private_key.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
    return private_key_bytes


def get_private_key_from_file_bytes(key: bytes, password: bytes = None):
    """
    Extracts a private key from the given byte sequence.

    This function attempts to extract a private key from the provided byte sequence
    by trying both PEM and DER formats.If a loader successfully loads the private key, it is returned.
    If neither format is successful, it raises an ValueError indicating an invalid private key.

    Args:
        key (bytes): The byte sequence containing the private key.
        password (optional): The password for the private key, if it is encrypted.

    Returns:
        The loaded private key if successful.

    Raises:
        ValueError: If the private key cannot be loaded by any of the loaders.
    """
    for loader in (get_private_key_from_pem, get_private_key_from_der):
        try:
            if private_key := loader(key, password):
                return private_key
        except Exception:
            continue
    raise ValueError("Invalid Private Key")


def get_private_key_from_pem(key_pem: bytes, password=None) -> PRIVATE_KEY_TYPES:
    """Get the Private Key from the PEM

    Args:
        key_pem (bytes): PEM Key to get the Private Key
        password (_type_, optional): Password to decrypt the Private Key. Defaults to None.

    Returns:
        PRIVATE_KEY_TYPES: Private Key generated from the PEM
    """
    return load_pem_private_key(key_pem, password)


def get_private_key_from_der(key_der: bytes, password=None) -> PRIVATE_KEY_TYPES:
    """Get the Private Key from the DER

    Args:
        key_der (bytes): DER Key to get the Private Key
        password (_type_, optional): Password to decrypt the Private Key. Defaults to None.

    Returns:
        PRIVATE_KEY_TYPES: Private Key generated from the DER
    """
    return load_der_private_key(key_der, password)


def get_public_key_from_file_bytes(key: bytes):
    """
    Extracts a public key from the given byte sequence.

    This function attempts to extract a public key from the provided byte sequence
    by trying both PEM and DER formats. If neither format is successful, it raises
    an assertion error indicating an invalid public key.
    Args:
        key (bytes): The byte sequence containing the public key.

    Returns:
        The extracted public key if successful.

    Raises:
        AssertionError: If the public key cannot be extracted from the byte sequence.
    """
    for loader in (get_public_key_from_pem, get_public_key_from_der):
        try:
            if public_key := loader(key):
                return public_key
        except Exception:
            continue
    raise ValueError("Invalid Public Key")


def get_public_key_from_pem(key_pem: bytes) -> PUBLIC_KEY_TYPES:
    """Get the Public Key from the PEM

    Args:
        key_pem (bytes): PEM Key to get the Public Key

    Returns:
        PUBLIC_KEY_TYPES: Public Key generated from the PEM
    """
    return load_pem_public_key(key_pem)


def get_public_key_from_der(key_der: bytes) -> PUBLIC_KEY_TYPES:
    """Get the Public Key from the DER

    Args:
        key_der (bytes): DER Key to get the Public Key

    Returns:
        PUBLIC_KEY_TYPES: Public Key generated from the DER
    """
    return load_der_public_key(key_der)


def get_public_key_from_numbers(key_type: KeyAlgorithms, pub_num: bytes) -> PUBLIC_KEY_TYPES:
    """
    Generates a public key object from the given key type and public numbers.

    Args:
        key_type (str): The type of the key. Supported values are 'ECCP521', 'ECCP384', 'ECCP256', 'ED25519',
            'RSA4096', 'RSA3072', and 'RSA2048'.
        pub_num (bytes): The public numbers in bytes format.

    Returns:
        PUBLIC_KEY_TYPES: The generated public key object corresponding to the provided key type and public numbers.

    Raises:
        ValueError: If the key_type is not supported.
    """
    if key_type.startswith('ECC'):
        curve_map = {
            KeyAlgorithms.ECC_P224: ec.SECP224R1(),
            KeyAlgorithms.ECC_P256: ec.SECP256R1(),
            KeyAlgorithms.ECC_SECP256_K1: ec.SECP256K1(),
            KeyAlgorithms.ECC_BRAINPOOL_P256_R1: ec.BrainpoolP256R1(),
            KeyAlgorithms.ECC_P384: ec.SECP384R1(),
            KeyAlgorithms.ECC_P521: ec.SECP521R1(),
        }
        if not (curve := curve_map.get(key_type)):
            raise ValueError(f"Unsupported ECC key type: {key_type}")
        split_size = len(pub_num) // 2
        x = int.from_bytes(pub_num[:split_size], 'big')
        y = int.from_bytes(pub_num[split_size:], 'big')
        public_key = ec.EllipticCurvePublicNumbers(x, y, curve).public_key()
    elif key_type in [KeyAlgorithms.RSA_1024, KeyAlgorithms.RSA_2048, KeyAlgorithms.RSA_3072, KeyAlgorithms.RSA_4096]:
        n = int.from_bytes(pub_num, 'big')
        public_key = rsa.RSAPublicNumbers(e=65537, n=n).public_key()
    elif key_type == KeyAlgorithms.ED25519:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_num)
    elif key_type == KeyAlgorithms.X25519:
        public_key = x25519.X25519PublicKey.from_public_bytes(pub_num)
    else:
        raise ValueError(f"Unsupported key type: {key_type}")
    return public_key


def get_private_pem(private_key: PRIVATE_KEY_TYPES, file: str = None) -> str:
    """
    Converts a private key to its PEM format and optionally writes it to a file.

    Args:
        private_key (PRIVATE_KEY_TYPES): The private key to be converted.
        file (str, optional): The file path where the PEM formatted key will be written. Defaults to None.

    Returns:
        str: The private key in PEM format as a string.
    """
    private_pem = private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ).decode('utf-8')
    if file:
        Path(file).write_text(private_pem)
    return private_pem


def get_public_pem(public_key: PUBLIC_KEY_TYPES, file: str = None):
    """
    Convert a public key to PEM format and optionally save it to a file.

    This function takes a public key object and converts it to a PEM-formatted string.
    If a file path is provided, the PEM string is written to the specified file.

    Args:
        public_key (PUBLIC_KEY_TYPES): The public key object to be converted to PEM format.
        file (str, optional): The file path where the PEM string should be saved. If not provided, the PEM string
                              is not written to a file.

    Returns:
        str: The PEM-formatted string representation of the public key.
    """
    public_pem = public_key.public_bytes(
        Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    if file:
        Path(file).write_text(public_pem)
    return public_pem


def generate_private_key(key: str = "", key_algo: KeyAlgorithms = KeyAlgorithms.ECC_P256) -> PRIVATE_KEY_TYPES:
    """
    Generates a private key based on the provided key or algorithm.

    If a key is provided and it exists as a file, the private key is read from the file.
    Otherwise, a new private key is generated using the specified algorithm.

    Args:
        key (str): The path to the key file or the key itself. Defaults to an empty string.
        key_algo (KeyAlgorithms): The algorithm to use for generating the key. Defaults to KeyAlgorithms.ECC_P256.

    Returns:
        PRIVATE_KEY_TYPES: The generated or retrieved private key.
    """
    if key:
        key = Path(key).read_bytes() if os.path.exists(key) else bytes.fromhex(key)
        private_key = get_private_key_from_file_bytes(key)
    else:
        private_key = generate_key_pair(key_algo)
    return private_key


def get_key_algo(key: Union[PRIVATE_KEY_TYPES, PUBLIC_KEY_TYPES]):
    """
    Determine the algorithm type of a given cryptographic key.

    Args:
        key (Union[PRIVATE_KEY_TYPES, PUBLIC_KEY_TYPES]): The cryptographic key for which the algorithm type is to be determined.
            This can be an instance of EllipticCurvePrivateKey, EllipticCurvePublicKey, RSAPrivateKey, RSAPublicKey,
            Ed25519PrivateKey, or Ed25519PublicKey.

    Returns:
        KeyAlgorithms: The algorithm type corresponding to the provided key.

    Raises:
        KeyError: If the key's curve name or key size is not found in the respective mapping dictionaries.
    """
    if isinstance(key, (ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey)):
        key_algo = CurveKeyAlgoMap[key.curve.name]
    elif isinstance(key, (rsa.RSAPrivateKey, rsa.RSAPublicKey)):
        key_algo = CurveKeyAlgoMap[key.key_size]
    elif isinstance(key, (ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey)):
        key_algo = KeyAlgorithms.ED25519

    return key_algo


def generate_symmetric_key(key_length: int) -> bytes:
    """
    Generates a symmetric key of the specified length.

    Args:
        key_length (int): The length of the symmetric key to generate in bytes.

    Returns:
        bytes: The generated symmetric key.
    """
    symmetric_key = os.urandom(key_length)
    return symmetric_key


def get_symmetric_pem(symm_key: bytes, file: str = None) -> None:
    """
    Encodes a symmetric key in PEM format and optionally writes it to a file.

    Args:
        symm_key (bytes): The symmetric key to be encoded.
        file (str, optional): The file path where the PEM encoded key will be written.
                              If not provided, the PEM key will not be written to a file.

    Returns:
        None
    """
    symmetric_key_base64 = base64.b64encode(symm_key).decode('ascii')
    pem_key = '-----BEGIN SYMMETRIC KEY-----\n'
    pem_key += symmetric_key_base64
    pem_key += '\n-----END SYMMETRIC KEY-----\n'
    if file:
        Path(file).write_text(pem_key)


def get_symmetric_key_from_pem(key_pem: Union[str, os.PathLike]) -> bytes:
    """
    Extracts and decodes a symmetric key from a PEM formatted string or file.

    Args:
        key_pem (Union[str, os.PathLike]): The PEM formatted symmetric key as a string or a path to a file containing the key.

    Returns:
        bytes: The decoded symmetric key.

    Raises:
        FileNotFoundError: If the provided path does not exist.
        ValueError: If the PEM content is not properly formatted or cannot be decoded.
    """
    if os.path.exists(key_pem):
        key_pem = Path(key_pem).read_text()
    key_pem = key_pem.replace('-----BEGIN SYMMETRIC KEY-----', '')
    key_pem = key_pem.replace("-----END SYMMETRIC KEY-----", '')
    key_pem = key_pem.replace("\n", "")
    key_pem = key_pem.replace("\r", "")
    return base64.b64decode(key_pem)
