# lsqr/backends/micro.py
"""
Ultra-lightweight backend for microcontrollers (STM32, ESP32, RISC-V).
Designed for < 100KB RAM usage.
"""

import struct
from typing import List, Union

class MicroBackend:
    """
    A minimal LSQ inference engine for embedded systems.
    - No dynamic allocation after init
    - Fixed-point optional
    - Bit-packing native support
    """

    def __init__(self, model_buffer: bytes):
        self.buf = model_buffer
        self.pos = 0
        self.layers = []
        self.current_input = None
        self._parse_model()

    def _read(self, fmt: str) -> tuple:
        sz = struct.calcsize(fmt)
        data = self.buf[self.pos:self.pos+sz]
        self.pos += sz
        return struct.unpack(fmt, data)

    def _parse_model(self):
        # Magic & Version
        magic = self.buf[self.pos:self.pos+3]; self.pos += 3
        assert magic == b'LSQ', "Invalid LSQ model"

        version, self.B = self._read('BB')  # Version, B
        self.C = self.B + 1
        layer_count, = self._read('I')

        for _ in range(layer_count):
            name_len, = self._read('H')
            name = self.buf[self.pos:self.pos+name_len].decode()
            self.pos += name_len

            rank, = self._read('B')
            shape = self._read(f'{rank}I')

            data_len, = self._read('I')
            data_start = self.pos
            data_end = self.pos + data_len
            self.pos += data_len

            padding, = self._read('B')

            self.layers.append({
                'name': name,
                'shape': shape,
                'data_slice': (data_start, data_end),
                'padding': padding
            })

    def set_input(self, input_data: List[float]):
        self.current_input = input_data

    def run_layer(self, index: int) -> List[float]:
        layer = self.layers[index]
        slice_start, slice_end = layer['data_slice']
        packed_data = self.buf[slice_start:slice_end]

        # Unpack bits
        total_bits = (layer['shape'][0] * layer['shape'][1]) * self.C
        num_codes = total_bits // self.C
        codes = self._unpack_micro(packed_data, self.C, num_codes, layer['padding'])

        # Decode using lookup table (precomputed in C)
        weights = [self._decode_code(code) for code in codes]
        weights = [w * 1.0 for w in weights]  # Placeholder for fixed-point later

        # Simple matrix multiplication (for demo)
        result = []
        in_features = len(self.current_input)
        W = [weights[i:i+in_features] for i in range(0, len(weights), in_features)]

        for row in W:
            val = sum(a * b for a, b in zip(self.current_input, row))
            result.append(max(val, 0))  # ReLU

        self.current_input = result
        return result

    def _unpack_micro(self, data: bytes, C: int, num_codes: int, padding: int) -> list:
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        if padding:
            bits = bits[:-padding]
        
        codes = []
        for i in range(0, len(bits), C):
            if i + C > len(bits):
                break
            code = 0
            for j in range(C):
                code = (code << 1) | bits[i + j]
            codes.append(code)
        return codes[:num_codes]

    def _decode_code(self, code: int) -> float:
        """Simulate LUT-based decoding (will be precomputed in real firmware)"""
        B = self.B
        n = (code >> B) & 1
        magnitude_part = code & ((1 << B) - 1)
        N = (1 << B) - magnitude_part
        try:
            magnitude = (1 / B) * (3.321928 * (B - (N).bit_length()))  # Approximate log2
        except:
            magnitude = 0.0
        return ((-1)**n) * magnitude
