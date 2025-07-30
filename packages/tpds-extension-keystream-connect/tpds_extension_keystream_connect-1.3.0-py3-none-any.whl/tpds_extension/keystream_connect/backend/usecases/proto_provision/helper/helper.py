# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
from cryptography.hazmat.primitives import hashes, hmac

from tpds.flash_program import FlashProgram
from tpds.api.api.hw.api_board import get_details


def check_board_status(board, logger):
    """Check the board status and program the factory hex if not programmed

    Args:
        board (_type_): Board information to check the status
        logger (_type_): Logger object to capture the logs
    """
    logger.log("Checking Board Status... ")
    assert board, "No board selected"
    board_info = get_details(board)
    kit_parser = FlashProgram(board, board_info)
    logger.log(kit_parser.check_board_status())
    assert kit_parser.is_board_connected(), "Check the Kit parser board connections"
    factory_hex = os.path.join(board_info.board_path, board, f"{board}.hex")
    if not kit_parser.is_factory_programmed():
        assert factory_hex, "Factory hex is unavailable to program"
        logger.log("Programming factory hex...")
        logger.log(f"Programming {factory_hex} file")
        kit_parser.load_hex_image_with_ipe(factory_hex)
    logger.log("Board Status OK")


def generate_diversified_key(salt: bytes, key: bytes):
    """
    Generate a diversified key using HMAC with SHA-256.

    This function takes a salt and a key as input and generates a diversified key using the HMAC
    algorithm with the SHA-256 hash function.

    Args:
        salt (bytes): The salt value used to diversify the key.
        key (bytes): The original key used in the HMAC process to generate the diversified key.

    Returns:
        bytes: The diversified key generated.
    """
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(salt)
    return h.finalize()
