from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


ext_modules = [Extension('CPyOracle', ['CPyOracle.pyx']),
               Extension('CTransition', ['CTransition.pyx']),
               Extension('CState', ['CState.pyx'])]

setup(
        cmdclass = {'build_ext': build_ext},
        ext_modules = ext_modules
)
