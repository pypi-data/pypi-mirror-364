import os
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

from definitions import VERSION


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPython3_EXECUTABLE={sys.executable}",
            f"-DPython3_ROOT_DIR={os.path.dirname(os.path.dirname(sys.executable))}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
            "-DBUILD_PYTHON_MODULE=ON",
            "-DBUILD_SHARED_LIB=OFF",
            "-DBUILD_STATIC_LIB=OFF",
            "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0",
        ]

        build_args = []
        
        # Platform-specific configuration
        if sys.platform.startswith("win"):
            cmake_args += [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}",
            ]
            if sys.maxsize > 2**32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:
            # Get number of CPUs for parallel build
            import multiprocessing
            build_args += ["--", f"-j{multiprocessing.cpu_count()}"]

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
    description="High-performance library for generating AWS S3 presigned URLs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    ext_modules=[CMakeExtension("libpresign")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    python_requires=">=3.8",
)