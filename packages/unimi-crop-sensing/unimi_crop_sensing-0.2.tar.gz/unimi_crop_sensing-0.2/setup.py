from setuptools import setup, find_packages

setup(
    name='unimi_crop_sensing',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'pyzed==5.0',
        'numpy',
        'scikit-image',
        'scikit-learn',
        'websocket'
])


