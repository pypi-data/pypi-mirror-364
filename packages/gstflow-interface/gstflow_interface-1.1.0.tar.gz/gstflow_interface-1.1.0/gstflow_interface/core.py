import numpy as np
import ctypes
from .lowlevel import _load_native_lib
from .types import GstflowBuffer, GstflowBufferLayout, GstflowDtypeMapper, GstflowLayoutMapper

def gstflow_process_image(image: np.ndarray) -> list[np.ndarray]:
    try: 
        lib = _load_native_lib()
        lib.gstflow_custom_process.argtypes = [ctypes.POINTER(GstflowBuffer), ctypes.POINTER(GstflowBuffer)]
        lib.gstflow_custom_process.restype = None
        lib.gstflow_free_buffer.argtypes = [ctypes.POINTER(GstflowBuffer)]
        lib.gstflow_free_buffer.restype = None

        h, w, c = image.shape
        dims = (ctypes.c_int * 4)(1, h, w, c)

        input_buf = GstflowBuffer()
        input_buf.data = image.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
        input_buf.name = b"python-input"
        input_buf.dims = dims
        input_buf.num_dims = 4
        input_buf.owns_self = False
        input_buf.owns_dims = False
        input_buf.owns_data = False
        input_buf.owns_name = False
        input_buf.layout = GstflowLayoutMapper.from_numpy_shape(image.shape)
        input_buf.dtype = GstflowDtypeMapper.get_dtype(image.dtype.type)

        output_buf = GstflowBuffer()
        lib.gstflow_custom_process(ctypes.byref(input_buf), ctypes.byref(output_buf))

        frames = []
        out_dims = [output_buf.dims[i] for i in range(output_buf.num_dims)]
        if output_buf.layout == GstflowBufferLayout.NHWC:
            shape = (out_dims[0], out_dims[1], out_dims[2], out_dims[3])
        elif output_buf.layout == GstflowBufferLayout.NCHW:
            shape = (out_dims[0], out_dims[3], out_dims[1], out_dims[2])
        else:
            raise ValueError(f"Unsupported layout: {output_buf.layout}")

        data = np.ctypeslib.as_array(output_buf.data, shape=(np.prod(shape),))
        frame_size = np.prod(shape[1:])  # size of each image

        for i in range(shape[0]):
            raw = data[i * frame_size: (i + 1) * frame_size]
            if output_buf.layout == GstflowBufferLayout.NHWC:
                frame = raw.reshape((shape[1], shape[2], shape[3]))
            elif output_buf.layout == GstflowBufferLayout.NCHW:
                frame = raw.reshape((shape[1], shape[2], shape[3])).transpose(1, 2, 0)
            frames.append(frame.copy())
        output_buf.owns_self = False
        lib.gstflow_free_buffer(ctypes.byref(output_buf))
        return frames

    except Exception as e:
        print("Error in gstflow_process_image:", e)
        return []
