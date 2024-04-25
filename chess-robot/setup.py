from setuptools import setup

setup(
    name='chess-robot', 
    version='1.0.0', 
    packages=['chess-robot'], 
    entry_points={
        'console_scripts': ['chess-robot = chess-robot.__main__.py']
    })

