import os
import platform
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from definitions import VERSION

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPython3_EXECUTABLE={sys.executable}",
            f"-DPython3_ROOT_DIR={os.path.dirname(os.path.dirname(sys.executable))}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
            "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            "-DBUILD_PYTHON_MODULE=ON",
            "-DBUILD_SHARED_LIB=OFF",
            "-DBUILD_STATIC_LIB=OFF",
        ]

        build_args = []
        
        # Platform-specific configuration
        if sys.platform.startswith("darwin"):
            # macOS
            if os.environ.get("ARCHFLAGS", "").find("x86_64") != -1:
                cmake_args.append("-DCMAKE_OSX_ARCHITECTURES=x86_64")
                cmake_args.append("-DCMAKE_OSX_DEPLOYMENT_TARGET=10.9")
            else:
                cmake_args.append("-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0")
        elif sys.platform.startswith("win"):
            cmake_args += [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}",
            ]
            if sys.maxsize > 2**32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:
            # Linux/Unix
            build_args += ["--", "-j", str(os.cpu_count() or 4)]

        # Set CMAKE_PREFIX_PATH for finding dependencies
        if "CMAKE_PREFIX_PATH" in os.environ:
            cmake_args += [f"-DCMAKE_PREFIX_PATH={os.environ['CMAKE_PREFIX_PATH']}"]

        # Create build directory
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Configure
        print(f"CMake configure command: cmake {ext.sourcedir} {' '.join(cmake_args)}")
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp
        )

        # Build
        subprocess.check_call(
            ["cmake", "--build", ".", "--config", cfg] + build_args,
            cwd=self.build_temp,
        )


# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="libpresign",
    version=VERSION,
    author="Your Name",
    author_email="your.email@example.com",
    description="High-performance library for generating AWS S3 presigned URLs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/libpresign",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/libpresign/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
    ],
    ext_modules=[CMakeExtension("libpresign")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    python_requires=">=3.8",
)