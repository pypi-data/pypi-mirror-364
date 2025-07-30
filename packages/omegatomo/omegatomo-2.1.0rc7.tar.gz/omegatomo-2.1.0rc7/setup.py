from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as build_py_orig

class CustomBuildPy(build_py_orig):
    def run(self):
        # Remove non-native shared libs
        import os
        import platform
        system = platform.system().lower()

        if system == "windows":
            # Remove .so
            so_path = os.path.join("omegatomo", "libs", "CPU_matrixfree_lib.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "CUDA_matrixfree_lib.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "OpenCL_matrixfree_lib.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "inveon.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "libRoot.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "OpenCL_matrixfree_uint16_lib.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "CUDA_matrixfree_uint16_lib.so")
            if os.path.exists(so_path):
                os.remove(so_path)
            so_path = os.path.join("omegatomo", "libs", "createSinogram.so")
            if os.path.exists(so_path):
                os.remove(so_path)
        elif system == "linux":
            # Remove .dll
            dll_path = os.path.join("omegatomo", "libs", "CPU_matrixfree_lib.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "CUDA_matrixfree_lib.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "OpenCL_matrixfree_lib.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "inveon.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "libRoot.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "OpenCL_matrixfree_uint16_lib.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "CUDA_matrixfree_uint16_lib.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
            dll_path = os.path.join("omegatomo", "libs", "createSinogram.dll")
            if os.path.exists(dll_path):
                os.remove(dll_path)
        super().run()

setup(
    name="omegatomo",
    version="2.1.0",
    packages=find_packages(),
    include_package_data=True,
    cmdclass={"build_py": CustomBuildPy},
    package_data={"omegatomo": ["CPU_matrixfree_lib.so", "CPU_matrixfree_lib.dll", "OpenCL_matrixfree_lib.so", "OpenCL_matrixfree_lib.dll", 
                                "CUDA_matrixfree_lib.so", "CUDA_matrixfree_lib.dll", "OpenCL_matrixfree_uint16_lib.so", "OpenCL_matrixfree_uint16_lib.dll", 
                                "CUDA_matrixfree_uint16_lib.so", "CUDA_matrixfree_uint16_lib.dll", "inveon.so", "inveon.dll", 
                                "libRoot.so", "libRoot.dll", "createSinogram.so", "createSinogram.dll"]},
)