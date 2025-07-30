# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.
import requests
from base64 import b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class KeyStream:
    """
    A client for interacting with the Kudelski IoT KeySTREAM API operations.

    This class handles authentication, device manager UID retrieval, and signing of digests using a specified key.

    Attributes:
        keystream_endpoint (str): Base URL for the KeySTREAM API.
        pub_uid (str): Public UID of the device profile.
        headers (dict): HTTP headers for API requests.
        dm_uid (str): Device Manager UID, retrieved based on the public UID.
    """
    def __init__(
        self,
        keystream_auth_token: str,
        pub_uid: str,
        keystream_endpoint: str = "https://mss.iot.kudelski.com",
    ):
        """
        Initializes the KTASign  with authentication and device profile information.

        Args:
            auth_token (str): Authorization token (API key) for KeySTREAM API.
            pub_uid (str): Public UID of the device profile.
            keystream_endpoint (str, optional): Base URL for the KeySTREAM API. Defaults to Kudelski's production endpoint.

        Raises:
            AssertionError: If the device manager UID cannot be retrieved.
        """
        self.keystream_endpoint = keystream_endpoint
        self.pub_uid = pub_uid
        self.headers = {
            "accept": "application/json",
            'x-correlation-id': 'ISEPDMUI-4d1cff76-7ace-4fda-0811-488fb8d99cbf',
            "Authorization": keystream_auth_token if keystream_auth_token.startswith("Basic ") else f"Basic {keystream_auth_token}",
        }
        self.dm_uuid = None
        self.get_dm_uuid()

    def get_dm_uuid(self):
        """
        Retrieves the Device Manager UID associated with the provided public UID.

        Sends a GET request to the KeySTREAM API to fetch the device manager information.

        Raises:
            AssertionError: If the request fails or the public UID is invalid.
        """
        get_dm_uuid_url = f"{self.keystream_endpoint}/dm?dpPublicUid={self.pub_uid}"
        get_dm_uuid_response = requests.get(url=get_dm_uuid_url, headers=self.headers)
        assert get_dm_uuid_response.status_code == 200, (
            "Connection Request Failed!!!\nPlease check \nDevice Public UID"
            "\nKeySTREAM Authorization Token (API Key) and its Validity and retry."
        )
        get_dm_uuid_response = get_dm_uuid_response.json()
        assert get_dm_uuid_response.get("totalRecords") != 0, \
            'Invalid public Profile UID!!!\n Please Provide Valid Device Fleet Profile Public UID'
        self.dm_uuid = get_dm_uuid_response.get("deviceManagers")[0].get("uuid")

    def sign(self, key_name: str, digest: bytes):
        """
        Requests a signature for the provided digest using the specified key.

        Args:
            key_name (str): The name of the key to use for signing.
            digest (bytes): The digest (hash) to be signed.

        Returns:
            dict: A dictionary containing:
                - "rawSignature" (bytes): The raw signature bytes.
                - "asn1Signature" (bytes): The ASN.1 encoded signature bytes.

        Raises:
            AssertionError: If the signing request fails.
        """
        sign_url = f"{self.keystream_endpoint}/lp/dm/{self.dm_uuid}/trustkeypairs/{key_name}/sign"
        sign_response = requests.post(url=sign_url, headers=self.headers, json={"digest": list(bytearray(digest))})
        sign_response_data = sign_response.json()
        assert sign_response.status_code == 200, f"Sigining Digest Failed with status {sign_response.status_code},\
             \nmessage{sign_response_data.get('message')}"
        return {
            "rawSignature": b64decode(sign_response_data.get("rawSignature")),
            "asn1Signature": b64decode(sign_response_data.get("asn1Signature"))
        }

    def get_trusted_pub_key(self, key_name: str):
        get_key_url = f"{self.keystream_endpoint}/lp/dm/{self.dm_uuid}/trustkeypairs/?name={key_name}"
        get_key_response = requests.get(url=get_key_url, headers=self.headers)
        get_key_response_data = get_key_response.json()
        assert get_key_response.status_code == 200, \
            f"Get Signing Key {key_name} failed with status {get_key_response.status_code}"
        keys = get_key_response_data.get("trustKeyPairs")[0]
        keys.update({
            "rawPublicKey": b64decode(keys.get("rawPublicKey")),
            "asn1PublicKey": b64decode(keys.get("asn1PublicKey"))
        })
        return keys

    def caluclate_digest(self, data: bytes, hash_algo: hashes.HashAlgorithm = hashes.SHA256()):
        """
        Calculates the SHA256 digest of given data.

        Args:
            data: The data to hash.

        Returns:
            A hexadecimal string representing the SHA256 digest.
        """
        digest = hashes.Hash(hash_algo, backend=default_backend())
        digest.update(data)
        return digest.finalize()
