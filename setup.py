from setuptools import setup, find_packages

version = '1.0'


setup(name='gpgkeys',
      version=version,
      description='Command line shell for GnuPG',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: Unix',
          'Operating System :: MacOS :: MacOS X',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: BSD License',
      ],
      keywords='gnupg shell',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/gpgkeys',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='gpgkeys.tests',
      install_requires=[
          'setuptools',
          'rl',
      ],
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
)

