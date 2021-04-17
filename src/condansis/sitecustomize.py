''' This file is invoked at python startup to modify the environment PATH so that some DLLs can be found 
'''
import os

prefix = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
#  Notice: this is where conda stores some DLLs. If that changes in the future, this here should also change
# Based on https://github.com/conda/conda-pack/blob/master/conda_pack/scripts/windows/activate.bat
os.environ["PATH"] = os.pathsep.join([
    os.path.join(prefix, 'Library', 'mingw-w64'),
    os.path.join(prefix, 'Library', 'usr', 'bin'),
    os.path.join(prefix, 'Library', 'bin')
]) + os.pathsep + os.environ["PATH"]