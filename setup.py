from setuptools import setup, find_packages

setup(
    name='stgt',
    version='1.0',
    packages=[''],
    url='',
    license='',
    author='Pablo Barbecho',
    author_email='pablo.barbecho@upc.edu',
    description='SUMO Traffic Generator Tool STGT',
    python_requires = '>=3.6',
    install_requires = ['PyQt5', 'shutil', 'psutil', 'tqdm', 'pandas','pathlib', 'uuid', 'scipy'],
    entry_points = {'console_scripts': ['stgt=stgt:DlgMain',],}

)
