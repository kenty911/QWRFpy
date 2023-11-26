from setuptools import setup, find_packages

INSTALL_REQUIRES = [
        'numpy',
        'matplotlib',
        'netCDF4',
        'cartopy',
        # wrf-python>=1.3.2,
]

setup(
    name='qwrfpy',
    packages=find_packages('qwrfpy'),\
    python_requires='>=3.7.0',
    version='2023.11.4',
    install_requires=INSTALL_REQUIRES,
    author_email = 'ken.314.papa@gmail.com',
    license='BSD 3-clause',
    long_description=open('README.md', encoding='UTF-8').read(),
    long_description_content_type="text/markdown",
    url = 'https://github.com/kenty911/QWRFpy',
    entry_points={"console_scripts":["wrfdraw = qwrfpy.WRFdraw:WRFdraw"]}
)
