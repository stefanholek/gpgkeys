from setuptools import setup, find_packages

version = '1.7.1'


setup(name='gpgkeys',
      version=version,
      description='Command line shell for GnuPG',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python :: 2',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License (GPL)',
      ],
      keywords='gnupg shell',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/gpgkeys',
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='gpgkeys.tests',
      install_requires=[
          'setuptools',
          'rl >= 1.4.1',
      ],
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
)

