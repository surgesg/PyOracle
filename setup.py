from distutils.core import setup
setup(name='pyoracle',
      version='01',
      author = 'Greg Surges',
      author_email = 'surgesg@gmail.com',
      py_modules = ['pyoracle', 
                    'Resources.DrawOracle', 
                    'Resources.helpers',
                    'Resources.PyOracle.IR',
                    'Resources.PyOracle.PyOracle',
                    'Resources.PyOracle.State',
                    'Resources.PyOracle.Transition']
    )
