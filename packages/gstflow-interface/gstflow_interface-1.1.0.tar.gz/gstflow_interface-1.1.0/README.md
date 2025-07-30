# gstflow\_interface

`gstflow_interface` is a lightweight Python module for interacting with native C/C++ libraries that implement the GSTFlow processing interface. It enables efficient image and video processing by bridging Python and native code.

## Features

* Interacts with native C/C++ libraries that implement `gstflow_custom_process`
* Handles buffer allocation and deallocation automatically
* Supports NumPy image arrays
* Easily integrates with automation pipelines or DeepStream applications

## Requirements

* Operating System: Linux
* Python 3.7 or higher
* NumPy
* A compiled shared library exposing the following functions:

  ```c
  void gstflow_custom_process(GstflowBuffer* input, GstflowBuffer* output);
  void gstflow_free_buffer(GstflowBuffer* buffer);
  ```

## Usage

### 1. Copy Header File

Copy the header file `gstflow_user_api.h` into your native project directory:

```bash
cp "$(python3 -c "import os, gstflow_interface; print(os.path.join(os.path.dirname(gstflow_interface.__file__), 'include', 'gstflow_user_api.h'))")" .
```

Include it in your C/C++ source:

```cpp
#include "gstflow_user_api.h"
```

### 2. Python Integration

```python
import os
import numpy as np
from gstflow_interface import gstflow_process_image

# Set the path to your compiled shared library
os.environ["GSTFLOW_USER_LIB"] = "/path/to/your/library.so"

# Example input image (NumPy array)
image = np.zeros((480, 640, 3), dtype=np.uint8)

# Process the image
output_images = gstflow_process_image(image)

# output_images is a list of NumPy arrays
```

---