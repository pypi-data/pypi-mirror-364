import os
import ctypes

def _load_native_lib():
    lib_path = os.environ.get("GSTFLOW_USER_LIB")
    if not lib_path or not os.path.exists(lib_path):
        raise RuntimeError("Environment variable GSTFLOW_USER_LIB is not set or path is invalid")
    return ctypes.CDLL(lib_path)