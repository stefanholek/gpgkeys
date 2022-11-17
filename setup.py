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
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: Implementation :: CPython',
      ],
      keywords='gnupg, gpg, gpg2, front-end, gpg shell, shell, REPL',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/stefanholek/gpgkeys',
      license='GPLv3',
      packages=find_packages(
          exclude=[
              'gpgkeys.tests',
          ],
      ),
      include_package_data=False,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'rl >= 3.1',
          'kmd >= 2.4',
          'term >= 2.4',
      ],
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
      project_urls={
          'Documentation': 'https://gpgkeys.readthedocs.io/en/stable/',
      },
      extras_require={
          'docs': [
              'sphinx == 5.3.0',
              'sphinx-rtd-theme == 1.0.0',
          ],
      },
)
