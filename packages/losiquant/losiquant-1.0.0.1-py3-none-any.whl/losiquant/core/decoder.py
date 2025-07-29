# lsqr/core/decoder.py
import numpy as np
import math

_LOGSIGNED_LUT = {}  # {B: lut_array}

def build_lut(B: int):
    """Build lookup table for LogSignedQuant decoding"""
    C = B + 1
    max_code = 1 << C
    lut = np.zeros(max_code, dtype=np.float32)
    
    for code in range(max_code):
        n = (code >> B) & 1  # sign bit
        magnitude_part = code & ((1 << B) - 1)
        N = (1 << B) - magnitude_part
        
        try:
            magnitude = (1 / B) * (math.log((1 << B) - N + 1e-9) / math.log(2))
        except (ValueError, OverflowError):
            magnitude = 0.0
        
        lut[code] = ((-1) ** n) * magnitude
    
    return lut

def logsigned_to_float_vectorized(codes: np.ndarray, B: int) -> np.ndarray:
    """Decode an array of codes using precomputed LUT"""
    global _LOGSIGNED_LUT
    if B not in _LOGSIGNED_LUT:
        _LOGSIGNED_LUT[B] = build_lut(B)
    
    lut = _LOGSIGNED_LUT[B]
    return lut[codes]
