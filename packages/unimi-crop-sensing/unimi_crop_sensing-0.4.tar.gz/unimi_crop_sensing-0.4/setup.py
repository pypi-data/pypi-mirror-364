from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='unimi_crop_sensing',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'pyzed==5.0',
        'numpy',
        'scikit-image',
        'scikit-learn',
        'websocket'
    ],
    long_description=description,
    long_description_content_type='text/markdown',
)