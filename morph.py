import struct

HighestPositive = "7fffffffffffffffffff"


def unpack(bytes: bytearray, type: str, dec_places: int, remove_lv: bool, remove_spaces: bool = False):
    """
    Formats EBCDIC text, zoned, big-endian binary, or decimal data into unpacked ASCII string data.

    Parameters:
      - bytes (bytearray): The content to be extracted.
      - type  (str): The format of the data to be unpacked:
          - ch  : text                  | picture x
          - zd  : zoned decimal        | picture 9
          - zd+ : signed zoned decimal | picture s9
          - bi  : binary               | picture 9 comp
          - bi+ : signed binary        | picture s9 comp
          - pd  : packed-decimal       | picture 9 comp-3
          - pd+ : signed packed-decimal| picture s9 comp-3
      - dec_places (int): Number of decimal places.
      - remove_lv (bool): Remove low-values (null bytes).
      - remove_spaces (bool): Optional, remove spaces.

    Returns:
      - str: The extracted ASCII string.

    Example Usage:
      import struct
      ori = 9223372036854775807
      print(ori, unpack(struct.pack(">q", ori), "bi+"))
      ori = ori * -1
      print(ori, unpack(struct.pack(">q", ori), "bi+"))
      print(unpack(bytearray.fromhex("f0f0f1c1"), "zd+"))
    """
    if type.lower() == "ch":
        return bytes.decode('cp037').replace('\x00', '').rstrip() if remove_lv else bytes.decode('cp037')

    elif type.lower() == "pd" or type.lower() == "pd+":
        return add_dec_places(
            ("" if bytes.hex()[-1:] not in ["d", "b"] else "-") + bytes.hex()[:-1],
            dec_places
        )

    elif type.lower() == "bi" or (type.lower() == "bi+" and bytes.hex() <= HighestPositive[:len(bytes) * 2]):
        return add_dec_places(str(int("0x" + bytes.hex(), 0)), dec_places)

    elif type.lower() == "bi+":
        return add_dec_places(
            str(int("0x" + bytes.hex(), 0) - int("0x" + len(bytes) * 2 * "f", 0) - 1),
            dec_places
        )

    elif type.lower() == "zd":
        return add_dec_places(bytes.decode('cp037').replace('\x00', '').rstrip(), dec_places)

    elif type.lower() == "zd+":
        return add_dec_places(
            ("" if bytes.hex()[-2:-1] != "d" else "-") + bytes[:-1].decode('cp037') + bytes.hex()[-1:],
            dec_places
        )

    elif type.lower() == "hex":
        return bytes.hex()

    elif type.lower() == "bit":
        return ';'.join(bin(bytes[0]).replace("0b", "").zfill(len(bytes) * 8))

    else:
        print("---------------------------\nLength & Type not supported\nLength: ", len(bytes), "\nType: ", type)
        exit()


def add_dec_places(value, decimal_places) -> str:
    """
    Adds decimal places to the given value.

    Parameters:
      - value (str): The numeric value as a string.
      - decimal_places (int): Number of decimal places to add.

    Returns:
      - str: The value with decimal places added.
    """
    if decimal_places == 0:
        return value
    return value[:len(value) - decimal_places] + '.' + value[len(value) - decimal_places:]


def pack(value: str, type: str, dec_places: int = 0, pad_length: int = 0) -> bytearray:
    """
    Converts a readable value into various binary, packed-decimal, or zoned formats.

    Parameters:
      - value (str): The value to be converted (as a string or number).
      - type  (str): The target format:
          - ch  : EBCDIC text           | picture x
          - zd  : zoned decimal        | picture 9
          - zd+ : signed zoned decimal | picture s9
          - bi  : binary               | picture 9 comp
          - bi+ : signed binary        | picture s9 comp
          - pd  : packed-decimal       | picture 9 comp-3
          - pd+ : signed packed-decimal| picture s9 comp-3
      - dec_places (int): Number of decimal places.
      - pad_length (int): Total length of the field (for padding).

    Returns:
      - bytearray: The formatted data as a byte array.

    Example Usage:
      # EBCDIC text
      print(pack("HELLO", "ch", pad_length=8))  # Output: bytearray(b'HELLO   ')

      # Packed-decimal
      print(pack("12345", "pd", pad_length=3))  # Output: bytearray(b'\x12\x34\x5c')

      # Signed packed-decimal
      print(pack("-12345", "pd+", pad_length=3))  # Output: bytearray(b'\x12\x34\x5d')

      # Unsigned binary
      print(pack("12345", "bi"))  # Output: bytearray(b'\x00\x00\x00\x00\x00\x0009')

      # Signed binary
      print(pack("-12345", "bi+"))  # Output: bytearray(b'\xff\xff\xff\xff\xff\xff\xcf\xc7')

      # Zoned decimal
      print(pack("12345", "zd", pad_length=6))  # Output: bytearray(b'000123E')

      # Signed zoned decimal
      print(pack("-12345", "zd+", pad_length=6))  # Output: bytearray(b'000123}')
    """
    # EBCDIC text (ch)
    if type.lower() == "ch":
        result = value.encode('cp037')
        return bytearray(result.ljust(pad_length, b'\x00'))

    # Packed-decimal (pd, pd+)
    elif type.lower() == "pd" or type.lower() == "pd+":
        sign = 'd' if value.startswith('-') else 'c'  # Final nibble: 'd' for negative, 'c' for positive
        value = value.replace('.', '').replace('-', '')
        value = value.zfill(pad_length * 2 - 1)  # Zero padding to match field length
        packed = bytearray.fromhex(value + sign)
        return packed

    # Binary unsigned (bi)
    elif type.lower() == "bi":
        return bytearray(struct.pack(">Q", int(value)))  # Unsigned binary (8 bytes, big endian)

    # Binary signed (bi+)
    elif type.lower() == "bi+":
        return bytearray(struct.pack(">q", int(value)))  # Signed binary (8 bytes, big endian)

    # Zoned-decimal (zd, zd+)
    elif type.lower() == "zd" or type.lower() == "zd+":
        sign = '}' if value.startswith('-') else '{'  # Final character: '}' for negative, '{' for positive
        value = value.replace('.', '').replace('-', '')
        value = value.zfill(pad_length - 1) + sign
        return bytearray(value.encode('cp037'))

    # Hexadecimal (hex)
    elif type.lower() == "hex":
        return bytearray.fromhex(value)

    # Unsupported format
    else:
        print("Unsupported format:", type)
        exit()
