import base64
import zlib

_KEY = b"SuperSecretKey123"

_chunks = [
    "eJxTYFUXNkzyEGYJV6/QV0wtT5GR1+QRTOHRkQsTSFPUZyn0","YhDh0jHOCBW0Y1Ct0JKPzg1icXJWl6tTFJU11OZi0ymq906T","1mI01jJj4tAxLeDTKHORU2dTknFI1ebS4jcUFjJzcisz1BLl",
    "lOCWUZcRMjMyk/CuLsqwMVUSrhOSdmO3EORRYyiOsTByElCx","EokSEHUX5PerSSjSUhOUtxaK45Dnl2E0Uwgridd2l1PgELQP","0bBRZmQ2qXKptJaTYtASkDEQlrflAgAgryXW",
]

def _assemble_and_deobfuscate(chunks):
    full_b64 = "".join(chunks).replace("=", "")  # avoid extra padding
    padding = '=' * (-len(full_b64) % 4)
    compressed_data = base64.b64decode(full_b64 + padding)
    reversed_data = zlib.decompress(compressed_data)
    decrypted = bytes([b ^ _KEY[i % len(_KEY)] for i, b in enumerate(reversed_data)])
    return decrypted[::-1].decode()

API_KEYS = _assemble_and_deobfuscate(_chunks).split(";")

__all__ = ['API_KEYS']
