# lsqr/core/bitpack.py
import numpy as np

def pack_bits(codes: np.ndarray, C: int) -> bytes:
    """
    Pack an array of C-bit codes into a byte stream.
    :param codes: 1D array of integers (each < 2^C)
    :param C: number of bits per code
    :return: packed bytes, padding (bits added at end)
    """
    bits = []
    for code in codes.flat:
        for i in range(C - 1, -1, -1):
            bits.append((code >> i) & 1)
    
    # Pad to multiple of 8
    padding = (8 - len(bits) % 8) % 8
    bits.extend([0] * padding)

    # Convert to bytes
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_val = 0
        chunk = bits[i:i+8]
        for bit in chunk:
            byte_val = (byte_val << 1) | bit
        byte_array.append(byte_val)
    
    return bytes(byte_array), padding


def unpack_bits(data: bytes, C: int, num_elements: int, padding: int = 0) -> np.ndarray:
    """
    Unpack a byte stream into an array of C-bit codes.
    :param data: packed bytes
    :param C: bits per code
    :param num_elements: total number of codes to extract
    :param padding: number of padded bits at the end
    :return: 1D array of codes
    """
    bits = []
    for byte in data:  # ✅ تم الإصلاح: for byte in data
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    
    # Remove padding
    if padding > 0:
        bits = bits[:-padding]
    
    codes = []
    for i in range(0, len(bits), C):
        if i + C > len(bits):
            break
        code = 0
        for j in range(C):
            code = (code << 1) | bits[i + j]
        codes.append(code)
    
    return np.array(codes[:num_elements], dtype=np.uint32)
