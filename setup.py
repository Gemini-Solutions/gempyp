from setuptools import find_packages, setup

setup(
    name='gempyp',
    version='1.0.60',
    packages=find_packages(),
    entry_points={
        'pytest11': [
            'gempyp = gempyp.gempyp_plugin',
        ]
    }
)
