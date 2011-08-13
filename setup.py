#
#Adodora setup script
#

from distutils.core import setup, Extension

asmhelper = Extension('asmhelper',
                      sources = ['src/asmhelper/asmhelper.c'])

setup(name = 'Apodora',
      version = '0.1',
      description = 'Python',
      ext_modules = [asmhelper])

