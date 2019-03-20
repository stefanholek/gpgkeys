import sys
import functools

from setuptools import setup, find_packages

version = '2.2'

if sys.version_info[0] >= 3:
    open = functools.partial(open, encoding='utf-8')


setup(name='gpgkeys',
      version=version,
      description='A GnuPG Shell',
      long_description=open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython',
      ],
      keywords='gnupg gpg gpg2 front-end shell',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/stefanholek/gpgkeys',
      license='GPLv3',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='gpgkeys.tests',
      install_requires=[
          'setuptools',
          'rl >= 3.0',
          'kmd >= 2.3',
          'term >= 2.3',
      ],
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
)
