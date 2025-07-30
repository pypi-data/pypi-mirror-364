import os
import platform
from setuptools import Extension, setup
from pathlib import Path
from definitions import VERSION

# Detect the platform
current_platform = platform.system()
is_arm_mac = current_platform == 'Darwin' and platform.machine() == 'arm64'

# Set compiler based on platform
if current_platform == 'Linux':
    os.environ["CC"] = "g++"
    os.environ["CXX"] = "g++"
elif current_platform == 'Darwin':  # macOS
    os.environ["CC"] = "clang++"
    os.environ["CXX"] = "clang++"
elif current_platform == 'Windows':
    os.environ["CC"] = "cl"
    os.environ["CXX"] = "cl"

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Platform-specific settings
extra_compile_args = ['-std=gnu++14']
extra_link_args = ['-std=gnu++14', '-lcrypto', '-ldl']
include_dirs = []
library_dirs = []

if current_platform == 'Linux':
    include_dirs.append('/usr/include')
    library_dirs.append('/usr/lib')
elif current_platform == 'Darwin':  # macOS
    if is_arm_mac:
        include_dirs.append('/opt/homebrew/opt/openssl@3/include')
        library_dirs.append('/opt/homebrew/opt/openssl@3/lib')
    else:
        include_dirs.append('/usr/local/include')
        library_dirs.append('/usr/local/lib')
    extra_compile_args.extend(['-mmacosx-version-min=10.9', '-stdlib=libc++'])
    extra_link_args.extend(['-mmacosx-version-min=10.9', '-stdlib=libc++'])
elif current_platform == 'Windows':
    include_dirs.append('C:/Program Files/OpenSSL-Win64/include')
    library_dirs.append('C:/Program Files/OpenSSL-Win64/lib')
    extra_compile_args = ['/std:c++14']
    extra_link_args = ['/LIBPATH:C:/Program Files/OpenSSL-Win64/lib', 'libcrypto.lib', 'libssl.lib']

setup(
    name='libpresign',
    version=VERSION,
    description='Package that just pre-signs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=[
        Extension(
            'libpresign',
            include_dirs=include_dirs,
            libraries=['crypto'],
            library_dirs=library_dirs,
            sources=['src/module.cpp', 'src/presign.cpp'],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args
        ),
    ],
)
