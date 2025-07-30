import ctypes
import numpy as np

class GstflowBufferLayout:
    NHWC = 0
    NCHW = 1
    CHW = 2
    NC = 3
    NCDHW = 4
    NDHWC = 5
    SEQ = 6
    NONE = 7

class GstflowDtype:
    UINT8 = 0
    INT8 = 1
    INT16 = 2
    UINT16 = 3
    INT32 = 4
    INT64 = 5
    FLOAT8 = 6
    BFLOAT16 = 7
    FLOAT16 = 8
    FLOAT32 = 9
    FLOAT64 = 10
    BOOL = 11
    NONE = 12

class GstflowBuffer(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_ubyte)),
        ("name", ctypes.c_char_p),
        ("dims", ctypes.POINTER(ctypes.c_int)),
        ("num_dims", ctypes.c_int),
        ("owns_self", ctypes.c_bool),
        ("owns_data", ctypes.c_bool),
        ("owns_dims", ctypes.c_bool),
        ("owns_name", ctypes.c_bool),
        ("layout", ctypes.c_int),
        ("dtype", ctypes.c_int),
    ]

class GstflowDtypeMapper:
    numpy_to_gstflow = {
        np.uint8: 0,    # GstflowDtype.UINT8
        np.int8: 1,
        np.int16: 2,
        np.uint16: 3,
        np.int32: 4,
        np.int64: 5,
        np.float16: 8,
        np.float32: 9,
        np.float64: 10,
        np.bool_: 11,
    }

    @staticmethod
    def get_dtype(np_dtype) -> int:
        dtype = GstflowDtypeMapper.numpy_to_gstflow.get(np_dtype)
        if dtype is None:
            raise ValueError(f"Unsupported NumPy dtype: {np_dtype}")
        return dtype

class GstflowLayoutMapper:
    @staticmethod
    def from_numpy_shape(shape: tuple[int]) -> int:
        if len(shape) == 3:
            # Most common: HWC
            return GstflowBufferLayout.NHWC
        elif len(shape) == 4:
            # Ambiguous: Could be NHWC or NCHW
            # You could add more heuristics here
            # Example: If shape[1] is small (<=4), assume NCHW
            if shape[1] <= 4:
                return GstflowBufferLayout.NCHW
            else:
                return GstflowBufferLayout.NHWC
        elif len(shape) == 2:
            # NC or CHW flattened
            return GstflowBufferLayout.NC
        else:
            raise ValueError(f"Unsupported NumPy shape for layout inference: {shape}")