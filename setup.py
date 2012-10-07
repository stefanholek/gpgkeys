import sys
import functools

from setuptools import setup, find_packages

version = '1.23'

if sys.version_info[0] >= 3:
    open = functools.partial(open, encoding='utf-8')


setup(name='gpgkeys',
      version=version,
      description='A GnuPG Shell',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords='gnupg gpg front-end shell',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/gpgkeys',
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      use_2to3=True,
      test_suite='gpgkeys.tests',
      install_requires=[
          'setuptools',
          'rl >= 2.4',
          'kmd >= 2.2',
          'term >= 2.0',
      ],
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
)
