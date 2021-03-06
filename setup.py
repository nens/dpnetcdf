from setuptools import setup

version = '0.5.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-extensions',
    'django-nose',
    'lizard-ui >= 4.0b5',
    'requests',
    'netCDF4',
    'BeautifulSoup',
    'pytz',
    'Pydap',
    'django-appconf',
    'lxml',
    'ipdb',
    'sqlalchemy',
    'geoalchemy',
    ],

tests_require = [
    'nose',
    'coverage',
    'mock',
    ]

setup(name='dpnetcdf',
      version=version,
      description=("Synchronisation and configuration of calculation results "
                   "within deltaportaal site."),
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Sander Smits',
      author_email='sander.smits@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['dpnetcdf'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
