"""Setup file for Storm Climatologies."""

from setuptools import setup

PACKAGE_NAMES = ['storm_climatologies', 'storm_climatologies.utils']
KEYWORDS = ['weather', 'meteorology', 'thunderstorm', '40-Dbz', 'tornado',
            '900 seconds']
SHORT_DESCRIPTION = (
    'Storm based catororizing and binning based on different characteristics')
LONG_DESCRIPTION = (
    'Storm Climatologies is a python package to help analyze storm tracks '
    'and observe there long term climatologies.')

CLASSIFIERS = ['Intended Audience :: Science/Research',
               'Programming Language :: Python :: 2.7']

PACKAGE_REQUIREMENTS = [
    'descartes', 'geopy', 'netCDF4', 'pyproj', 'scipy', 'sharppy', 'skewt',
    'scikit-learn', 'matplotlib', 'numpy', 'pandas', 'shapely', 'scikit-image']

# PACKAGE_REQUIREMENTS = [
#     'descartes', 'geopy==1.11.2', 'netCDF4==1.2.4', 'pyproj==1.9.5.1',
#     'scipy==0.19.0', 'sharppy==1.3.0', 'skewt==0.1.4r2',
#     'scikit-learn==0.18.1', 'opencv==3.1.0', 'matplotlib==2.0.2',
#     'numpy==1.11.3', 'pandas==0.21.0', 'shapely==1.5.16',
#     'scikit-image==0.13.0']

if __name__ == '__main__':
    setup(name='Storm_Climatologies', version='0.1', description=SHORT_DESCRIPTION,
          author='Aodhan Sweeney', author_email='ajs15e@my.fsu.edu',
          long_description=LONG_DESCRIPTION,
          url='https://github.com/AodhanSweeney/Storm-Climatologies',
          packages=PACKAGE_NAMES, scripts=[], keywords=KEYWORDS,
          classifiers=CLASSIFIERS, include_package_data=True, zip_safe=False,
          install_requires=PACKAGE_REQUIREMENTS)
