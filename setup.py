from setuptools import setup, find_packages

from light_by_light import __version__

setup(
    name='lbl_botorch',
    version=__version__,

    url='https://github.com/maxbalrog/light-by-light-botorch',
    author='Maksim Valialshchikov',
    author_email='maksim.valialshchikov@uni-jena.de',

    packages=find_packages(exclude=['tests', 'tests.*', 'runs', 'runs.*',
                                    'bash_scripts', 'bash_scripts.*',
                                    'cluster', 'cluster.*']),

    # install_requires=[
    # 'pytest>=4',
    # 'pytest-cov>=2',
    # ]
)
