from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='unimi_crop_sensing',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'pyzed==5.0',
        'numpy',
        'scikit-image',
        'scikit-learn',
        'websocket'
    ],
    description='A toolkit for crop sensing using the ZED camera',
    long_description=description,
    long_description_content_type='text/markdown',
)