from setuptools import setup, find_packages

version = '2.3'


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
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: Implementation :: CPython',
      ],
      keywords='gnupg, gpg, gpg2, front-end, gpg shell, shell, REPL',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/stefanholek/gpgkeys',
      license='GPL-3.0-or-later',
      packages=find_packages(
          exclude=[
              'gpgkeys.tests',
          ],
      ),
      include_package_data=False,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'rl >= 3.2',
          'kmd >= 2.4',
          'term >= 2.5',
      ],
      python_requires='>=3.8',
      entry_points = {
          'console_scripts': 'gpgkeys=gpgkeys.gpgkeys:main',
      },
      project_urls={
          'Documentation': 'https://gpgkeys.readthedocs.io/en/stable/',
      },
      extras_require={
          'docs': [
              'sphinx == 9.1.0',
              'sphinx-rtd-theme == 3.1.0',
          ],
      },
)
