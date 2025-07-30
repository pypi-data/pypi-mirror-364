import ctypes
import os
import glob

# Load the shared library libdars*.so or libdars*.dll or libdars*.pyd
# Supose the shared library is in the same directory as this script.

lib_dir = os.path.dirname(os.path.abspath(__file__))
# lib_path = glob.glob("./libdars*.so",root_dir=lib_dir) #python > 3.10
lib_path = glob.glob(lib_dir + "/libdars*.so")
if len(lib_path) == 0:
    lib_path = glob.glob(lib_dir + "/libdars*.pyd")
if len(lib_path) == 0:
    lib_path = glob.glob(lib_dir + "/libdars*.dll")
if len(lib_path) == 0:
    raise FileNotFoundError("Shared library libdars*.so, libdars*.pyd or libdars*.dll not found.")
lib_path = os.path.join(os.path.dirname(__file__), lib_path[0])
print(f"Loading shared library from {lib_path}")
if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Shared library {lib_path} not found.")
# Load the shared library using ctypes
try:
    libdars=ctypes.CDLL(lib_path)
    #libdars=ctypes.CDLL(lib_path, ctypes.RTLD_GLOBAL)
except OSError as e:
    raise OSError(f"Could not load shared library {lib_path}: {e}")
# Check if the library has the required function
try:
    libdars.dars
except AttributeError:
    raise AttributeError(f"Function dars not found in {lib_path}")
try:
    libdars.osc_aa
except AttributeError:
    raise AttributeError(f"Function osc_aa not found in {lib_path}")

from .dars import dars, osc_aa

__all__ = ['dars', 'osc_aa']
