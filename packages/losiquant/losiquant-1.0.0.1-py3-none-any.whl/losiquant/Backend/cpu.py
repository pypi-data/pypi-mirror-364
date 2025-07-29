# lsqr/backends/cpu.py
"""
Lightweight CPU backend for LSQ models.
Designed for high efficiency and easy Cython/C++ conversion.
"""
import numpy as np
from typing import Dict, Tuple, Optional
from ...core.decoder import logsigned_to_float_vectorized

class CPUTensor:
    """CPU-side tensor with LSQ storage"""
    def __init__(self, data: np.ndarray, shape: tuple, B: int):
        self.data = data      # uint8/16/32 or bit-packed bytes
        self.shape = shape
        self.B = B
        self.C = B + 1
        self._decoded = None

    def decode(self) -> np.ndarray:
        if self._decoded is not None:
            return self._decoded
        
        if isinstance(self.data, bytes):
            from ...core.bitpack import unpack_bits
            total_elements = int(np.prod(self.shape))
            codes = unpack_bits(self.data, self.C, total_elements)
            codes = codes.reshape(self.shape)
        else:
            codes = self.data
        
        self._decoded = logsigned_to_float_vectorized(codes, self.B)
        return self._decoded


class CPUModelRunner:
    """
    Minimal inference runner for LSQ-quantized models.
    Supports Linear and Conv2d operations.
    """
    def __init__(self):
        self.layers = []
        self.activations = []

    def add_linear(self, weight: CPUTensor, bias: Optional[np.ndarray] = None):
        self.layers.append(('linear', weight, bias))

    def add_conv2d(self, weight: CPUTensor, bias: Optional[np.ndarray] = None,
                   stride=1, padding=0, dilation=1, groups=1):
        self.layers.append(('conv2d', weight, bias, stride, padding, dilation, groups))

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.activations = [x.astype(np.float32)]

        for layer in self.layers:
            op = layer[0]
            weight_tensor = layer[1]
            bias = layer[2]

            W = weight_tensor.decode()

            if op == 'linear':
                x = x @ W.T
                if bias is not None:
                    x += bias
                x = np.maximum(x, 0)  # ReLU

            elif op == 'conv2d':
                stride, pad, dil, grp = layer[3], layer[4], layer[5], layer[6]
                x = self._conv2d(x, W, bias, stride, pad, dil, grp)
                x = np.maximum(x, 0)  # ReLU

            self.activations.append(x)

        return x

    def _conv2d(self, x: np.ndarray, weight: np.ndarray, bias: Optional[np.ndarray],
                stride: int, padding: int, dilation: int, groups: int) -> np.ndarray:
        from scipy.signal import convolve
        N, C_in, H, W = x.shape
        C_out, _, KH, KW = weight.shape
        OH = (H + 2*padding - KH) // stride + 1
        OW = (W + 2*padding - KW) // stride + 1
        out = np.zeros((N, C_out, OH, OW), dtype=np.float32)

        # Padding
        x_pad = np.pad(x, ((0,), (0,), (padding,), (padding,)), mode='constant')

        for n in range(N):
            for c_out in range(C_out):
                for c_in_group in range(C_in // groups):
                    c_in = c_out // (C_out // groups) * (C_in // groups) + c_in_group
                    filt = weight[c_out, c_in]
                    conv_result = convolve(x_pad[n, c_in], filt, mode='valid')
                    out[n, c_out] += conv_result[::stride, ::stride]

        if bias is not None:
            out += bias.reshape(1, -1, 1, 1)

        return out
