# lsqr/core/engine.py
import torch
import torch.nn as nn
import numpy as np
from ..core.decoder import logsigned_to_float_vectorized
from ..core.bitpack import unpack_bits

class LSQTensor:
    def __init__(self, data, shape, B: int, storage_type: str, padding: int = 0):
        self.data = data  # tensor أو bytes
        self.shape = tuple(shape)
        self.B = B
        self.C = B + 1
        self.storage_type = storage_type  # 'uint8', 'uint16', 'uint32', 'bit_packed'
        self.padding = padding

    def decode(self) -> torch.Tensor:
        if self.storage_type == 'bit_packed':
            codes_np = unpack_bits(
                self.data, self.C, np.prod(self.shape), self.padding
            )
            codes_np = codes_np.reshape(self.shape)
        else:
            codes_np = self.data.cpu().numpy()
        
        float_data = logsigned_to_float_vectorized(codes_np, self.B)
        return torch.from_numpy(float_data).to(self.data.device)


class LSQLinear(nn.Module):
    def __init__(self, weight: LSQTensor, bias: torch.Tensor = None):
        super().__init__()
        self.weight = weight
        self.bias = bias if bias is not None else None
        self._cached_weight = None

    def forward(self, x):
        if self._cached_weight is None:
            self._cached_weight = self.weight.decode()
        return torch.nn.functional.linear(x, self._cached_weight, self.bias)


class LSQConv2d(nn.Module):
    def __init__(self, weight: LSQTensor, bias: torch.Tensor = None, 
                 stride=1, padding=0, dilation=1, groups=1):
        super().__init__()
        self.weight = weight
        self.bias = bias
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.groups = groups
        self._cached_weight = None

    def forward(self, x):
        if self._cached_weight is None:
            self._cached_weight = self.weight.decode()
        return torch.nn.functional.conv2d(
            x, self._cached_weight, self.bias,
            self.stride, self.padding, self.dilation, self.groups
        )
