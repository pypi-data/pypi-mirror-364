#ifndef GSTFLOW_USER_API_H
#define GSTFLOW_USER_API_H

#ifdef __cplusplus
extern "C" {
#endif

// -----------------------------------------------------------------------------
// GSTFlow Framework - User API Definitions
//
// This header defines data types and helper functions required to implement
// custom processing modules within the GSTFlow framework.
//
// NOTE: DO NOT MODIFY these definitions unless you fully control both the
//       plugin and the core framework integration.
// -----------------------------------------------------------------------------

typedef enum {
    NHWC,
    NCHW,
    CHW,
    NC,
    NCDHW,
    NDHWC,
    SEQ,
    NONE
} GstflowBufferLayout;
enum class GstflowDtype {
    UINT8,
    INT8,
    INT16,
    UINT16,
    INT32,
    INT64,
    FLOAT8,    
    BFLOAT16,   
    FLOAT16,
    FLOAT32,
    FLOAT64,
    BOOL,
    NONE
};
typedef struct {
    unsigned char* data;          // Pointer to raw tensor data
    char* name;                   // Optional identifier or label
    int* dims;                    // Dimensions of a single tensor (e.g., [h, w, c] or [c, h, w])
    int num_dims;                 // Number of dimensions
    bool owns_self, owns_data, owns_dims, owns_name;
    GstflowBufferLayout layout;
    GstflowDtype dtype;
} GstflowBuffer;

// -----------------------------------------------------------------------------
// gstflow_custom_process
//
// Custom user-defined processing function. The GSTFlow framework will call
// this function with input and output buffers.
//
// This must be defined in user code with C linkage for dynamic loading.
// -----------------------------------------------------------------------------
void gstflow_custom_process(
    GstflowBuffer* input,
    GstflowBuffer* output
);
// -----------------------------------------------------------------------------
// gstflow_free_buffer
//
// Utility function to safely free buffer data allocated by the user or
// processing logic. Declared inline to allow use in headers.
// -----------------------------------------------------------------------------
#ifdef __cplusplus
#include <cstdlib>
#else
#include <stdlib.h>
#endif
void gstflow_free_buffer(GstflowBuffer* buffer);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // GSTFLOW_USER_API_H
