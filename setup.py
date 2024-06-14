# Adapted from https://github.com/pybind/cmake_example/blob/master/setup.py
import importlib
import os
import platform
import subprocess
import sys
from sysconfig import get_paths

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir, build_with_cuda):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.build_with_cuda = build_with_cuda


class Build(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        super().run()

    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            info = get_paths()
            include_path = info['include']
            cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                          '-DPYTHON_INCLUDE_PATH=' + include_path]

            cfg = 'Debug' if self.debug else 'Release'
            build_args = ['--config', cfg]

            if platform.system() == "Windows":
                cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir),
                               '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
                if sys.maxsize > 2 ** 32:
                    cmake_args += ['-A', 'x64']
                build_args += ['--', '/m']
            else:
                cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
                build_args += ['--', '-j8']

            if ext.build_with_cuda:
                cmake_args += ['-DDIFFVG_CUDA=1']
            else:
                cmake_args += ['-DDIFFVG_CUDA=0']

            env = os.environ.copy()
            env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                                  self.distribution.get_version())
            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
            subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        else:
            super().build_extension(ext)


torch_spec = importlib.util.find_spec("torch")
tf_spec = importlib.util.find_spec("tensorflow")
packages = []
build_with_cuda = False
build_for_TF = False
if torch_spec is not None:
    packages.append('pydiffvg')
    import torch

    if torch.cuda.is_available():
        build_with_cuda = True
if tf_spec is not None and sys.platform != 'win32' and build_for_TF:
    packages.append('pydiffvg_tensorflow')
    if not build_with_cuda:
        import tensorflow as tf

        if tf.test.is_gpu_available(cuda_only=True, min_cuda_compute_capability=None):
            build_with_cuda = True
if len(packages) == 0:
    print('Error: PyTorch or Tensorflow must be installed. For Windows platform only PyTorch is supported.')
    exit()
# Override build_with_cuda with environment variable
if 'DIFFVG_CUDA' in os.environ:
    build_with_cuda = os.environ['DIFFVG_CUDA'] == '1'

TEMPLATE_ = "%%template%%"
gpu_architecture = ""
if build_with_cuda:
    # Only for torch:
    try:
        import torch

        gpu_name = torch.cuda.get_device_name()
        if gpu_name == "Tesla T4":
            gpu_architecture = "-gencode=arch=compute_75,code=sm_75"
        elif gpu_name == "Tesla K80":
            gpu_architecture = "-gencode=arch=compute_37,code=sm_37"
        elif gpu_name == "GeForce RTX 3090":
            gpu_architecture = "-gencode=arch=compute_86,code=sm_86"
        elif gpu_name == "GeForce RTX 4090":
            gpu_architecture = "-arch=sm_89 -gencode=arch=compute_89,code=sm_89 -gencode=arch=compute_89,code=compute_89"
        else:
            print(f"GPU `{gpu_name}` is unknown => using GPU can cause errors, set manually architecture.")
            print("Find more info here: "
                  "https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/")
    except:
        print("Are you sure torch/CUDA is installed?")

if 'RTX_3090' in os.environ:
    build_with_cuda = os.environ['RTX_3090'] == '1'
    gpu_architecture = "-gencode=arch=compute_86,code=sm_86"
elif 'RTX_4090' in os.environ:
    build_with_cuda = os.environ['RTX_4090'] == '1'
    gpu_architecture = "-arch=sm_89 -gencode=arch=compute_89,code=sm_89 -gencode=arch=compute_89,code=compute_89"

with open("CMakeLists_template.txt", 'r') as f:
    template = f.read()
with open("CMakeLists.txt", 'w') as f:
    f.write(template.replace(TEMPLATE_, gpu_architecture))

setup(name='diffvg',
      version='0.0.1',
      install_requires=["svgpathtools"],
      description='Differentiable Vector Graphics',
      ext_modules=[CMakeExtension('diffvg', '', build_with_cuda)],
      cmdclass=dict(build_ext=Build, install=install),
      packages=packages,
      zip_safe=False)
if sys.platform == "win32":
    print("*" * 50)
    print("ATTENTION!!!")
    print(f"Rename the `your_venv\lib\site-packages\diffvg-0.0.1-_some_versions_\diffvg` file to `diffvg.pyd`!")
