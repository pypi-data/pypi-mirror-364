# lsqr/formats/lsq_model.py
import struct
import torch
from ..core.bitpack import pack_bits, unpack_bits
from ..core.engine import LSQTensor

_MAGIC = b'LSQ'
_VERSION = 1

def save_lsq_model(state_dict: dict, B: int, filepath: str):
    with open(filepath, 'wb') as f:
        f.write(_MAGIC)
        f.write(struct.pack('B', _VERSION))
        f.write(struct.pack('B', B))
        
        tensor_count = len(state_dict)
        f.write(struct.pack('I', tensor_count))

        for name, tensor in state_dict.items():
            if isinstance(tensor, LSQTensor):
                # كتابة اسم الطبق
                name_bytes = name.encode('utf-8')
                f.write(struct.pack('H', len(name_bytes)))
                f.write(name_bytes)

                # الشكل
                shape = tensor.shape
                f.write(struct.pack('B', len(shape)))
                f.write(struct.pack(f'{len(shape)}I', *shape))

                # البيانات
                if tensor.storage_type == 'bit_packed':
                    packed_data, padding = pack_bits(tensor.data, tensor.C)
                    f.write(struct.pack('I', len(packed_data)))
                    f.write(packed_data)
                    f.write(struct.pack('B', padding))
                else:
                    # حفظ كمصفوفة طبيعية
                    flat_data = tensor.data.flatten().cpu().numpy()
                    packed_data, padding = pack_bits(flat_data, tensor.C)
                    f.write(struct.pack('I', len(packed_data)))
                    f.write(packed_data)
                    f.write(struct.pack('B', padding))


def load_lsq_model(filepath: str):
    with open(filepath, 'rb') as f:
        magic = f.read(3)
        if magic != _MAGIC:
            raise ValueError("Not a valid LSQ file")
        
        version = struct.unpack('B', f.read(1))[0]
        B = struct.unpack('B', f.read(1))[0]
        tensor_count = struct.unpack('I', f.read(4))[0]

        state_dict = {}
        for _ in range(tensor_count):
            # اسم الطبق
            name_len = struct.unpack('H', f.read(2))[0]
            name = f.read(name_len).decode('utf-8')

            # الشكل
            rank = struct.unpack('B', f.read(1))[0]
            shape = struct.unpack(f'{rank}I', f.read(4 * rank))

            # البيانات
            data_len = struct.unpack('I', f.read(4))[0]
            data_bytes = f.read(data_len)
            padding = struct.unpack('B', f.read(1))[0]

            # فك الحزمة
            total_elements = int(torch.prod(torch.tensor(shape)))
            codes = unpack_bits(data_bytes, B + 1, total_elements, padding)
            codes = codes.reshape(shape)

            # إنشاء LSQTensor
            if codes.nbytes <= 2**16:
                dtype = torch.uint16
            elif codes.nbytes <= 2**32:
                dtype = torch.uint32
            else:
                dtype = torch.uint64

            codes_torch = torch.from_numpy(codes.astype(np.uint32))
            storage = 'bit_packed' if (B+1) not in [8, 16, 32] else (
                'uint8' if B+1 == 8 else 'uint16' if B+1 == 16 else 'uint32'
            )

            state_dict[name] = LSQTensor(
                data=codes_torch if storage != 'bit_packed' else data_bytes,
                shape=shape,
                B=B,
                storage_type=storage,
                padding=padding
            )

        return state_dict, B
