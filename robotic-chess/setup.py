from setuptools import setup

setup(
    name='robotic-chess', 
    version='1.0.0', 
    packages=['robotic-chess'], 
    entry_points={
        'console_scripts': ['robotic-chess = robotic-chess.__main__.py']
    })

