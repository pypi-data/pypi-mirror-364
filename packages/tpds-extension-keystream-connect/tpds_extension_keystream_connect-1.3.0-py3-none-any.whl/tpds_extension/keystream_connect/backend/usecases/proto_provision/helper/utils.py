# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.


def get_c_hex(value: bytes) -> str:
    """
    Converts a byte array into a formatted string of C-style hexadecimal values.

    Args:
        value (bytes): The byte array to be converted.

    Returns:
        str: A string containing the C-style hexadecimal representation of the byte array,
             with each byte formatted as "0xXX" and grouped in lines of 16 bytes.
    """
    hex_bytes = ""
    for x in range(0, len(value), 16):
        hex_bytes += "".join(["0x%02X, " % y for y in value[x: x + 16]]) + "\n"
    return hex_bytes


def get_c_array(var_name: str, data: bytes) -> str:
    """
    Generates a C array definition from the given variable name and byte data.

    Args:
        var_name (str): The name of the C array variable.
        data (bytes): The byte data to be converted into a C array.

    Returns:
        str: A string containing the C array definition, including the length
             of the array and the array elements in hexadecimal format.
    """
    return (
        f"#define {var_name.upper()}_LEN {len(data)}\n\n"
        f"const uint8_t {var_name}[{var_name.upper()}_LEN] = " + "{\n"
        f"{get_c_hex(data)}" + "};\n\n"
    )
