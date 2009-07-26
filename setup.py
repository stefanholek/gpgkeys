from setuptools import setup, find_packages, Extension
from os.path import join, exists
from sys import platform

version = '1.0'


include_dirs = []
library_dirs = []

if platform == 'darwin':
    # MacPorts
    if exists('/opt/local/include'):
        include_dirs += ['/opt/local/include']
        library_dirs += ['/opt/local/lib']


completion = \
Extension(name='_readline',
          sources=[join('gpgkeys', '_readline.c')],
          libraries=['readline', 'ncursesw'],
          include_dirs=include_dirs,
          library_dirs=library_dirs,
)


setup(name='gpgkeys',
      version=version,
      description='Command line shell for GnuPG',
      #long_description=open('README.txt').read() + '\n' +
      #                 open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='gnupg shell',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/gpgkeys',
      license='Python',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      test_suite='gpgkeys.tests',
      ext_modules=[
          completion,
      ],
      install_requires=[
          'setuptools',
          'setuptools_hg',
      ],
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
)

