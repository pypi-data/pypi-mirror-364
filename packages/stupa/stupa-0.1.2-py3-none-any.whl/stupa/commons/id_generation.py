import time
import struct
import secrets

class ULIDPyGenerator:
    ENCODING = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'  # Base32 encoding
    RANDOM_BITS = 80
    ENCODED_LENGTH = 26

    @staticmethod
    def generate_ulid(prefix='', time_val=None):
        if time_val is None:
            time_val = time.time()

        ulid_bytes = ULIDPyGenerator.generate_bytes_ulid(time_val)
        ulid_str = ULIDPyGenerator.encode_ulid(ulid_bytes)

        if prefix:
            ulid_str = prefix + ulid_str[len(prefix):]

        return ulid_str

    @staticmethod
    def generate_bytes_ulid(time_val):
        if time_val is None:
            time_val = time.time()

        # Generate 10 bytes of randomness
        random_bytes = secrets.token_bytes(ULIDPyGenerator.RANDOM_BITS // 8)

        # Pack time as 48 bits (6 bytes)
        time_bytes = struct.pack('>Q', int(time_val * 1000))[2:]

        return time_bytes + random_bytes

    @staticmethod
    def encode_ulid(ulid_bytes):
        ulid_int = int.from_bytes(ulid_bytes, byteorder='big')
        encoded = []

        while ulid_int > 0:
            encoded.append(ULIDPyGenerator.ENCODING[ulid_int % 32])
            ulid_int //= 32

        while len(encoded) < ULIDPyGenerator.ENCODED_LENGTH:
            encoded.append('0')

        return ''.join(reversed(encoded))