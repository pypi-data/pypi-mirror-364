# Libpresign

Single-purpose library created for generating AWS S3 presigned URLs fast.

Implemented in C++ using OpenSSL 3.1.

## Moto

Boto3 is heavy dependency if you just want to create a presigned URL. And it's famously slow.

## How to use

```python3
import libpresign

libpresign.get(
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "region-1",
    "bucket-name", 
    "object-key.txt",
    3600,  # Expiration time in seconds
)
```
Output
```text
'https://bucket.s3.amazonaws.com/object-key.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=creds1%2F20230711%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Date=20230711T125101Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=5c5a2e2858261266db950e4912fb12ffcd5d0bcf40d873bf9fe209ee789f6c86'
```

### Example with MinIO or custom S3-compatible endpoint

```python3
import libpresign

# For MinIO or other S3-compatible services
libpresign.get(
    "minioadmin",
    "minioadmin",
    "us-east-1",
    "bucket-name", 
    "object-key.txt",
    3600,
    "localhost:9000"  # MinIO endpoint
)
```

### Function signature
```python3
def get(
    access_key_id: str,
    secret_access_key: str,
    region: Optional[str],  # defaults to "us-east-1"
    bucket: str,
    key: str,
    expires: Optional[int], # defaults to 3600 (1h)
    endpoint: Optional[str], # defaults to "s3.amazonaws.com"
):
    ...
```

## Comparison to boto3

### Test case

Generate 10 000 presigned URLs. Compare execution times

### Results
```text
┌────────────────────────┬────────┬────────────┐
│ library                │ boto3  │ libpresign │
├────────────────────────┼────────┼────────────┤
│ avg execution time, μs │ 2232.3 │ 13.9       │ 
└────────────────────────┴────────┴────────────┘
```

Libpresign came out to be 160 times faster

## Dependencies

* C++ Compiler (GCC, Clang, or MSVC)
* CMake 3.15+
* OpenSSL 3.x
* Python 3.8+ (for Python bindings)

## Building from Source

### Using CMake (Recommended)

```bash
# Create build directory
mkdir build && cd build

# Configure
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build .

# Install (optional)
cmake --install .
```

### CMake Options

- `BUILD_PYTHON_MODULE` (ON/OFF): Build Python extension module (default: ON)
- `BUILD_SHARED_LIB` (ON/OFF): Build standalone shared library (default: OFF)  
- `BUILD_STATIC_LIB` (ON/OFF): Build standalone static library (default: OFF)

### Building Python Wheels

```bash
# Using CMake-based setup
python setup_cmake.py bdist_wheel

# Or use the convenience script
./build-wheels-cmake.sh
```

### Legacy Build Method

The original setuptools-based build is still available:

```bash
python setup.py build_ext --inplace
```
