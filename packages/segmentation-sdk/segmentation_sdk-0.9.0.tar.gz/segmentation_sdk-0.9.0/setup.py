from setuptools import setup, find_packages
setup(
    name='segmentation_sdk',
    version='0.9.0',
    description='A segmentation utilities SDK for ML pipelines',
    author='Saurav Kumar',
    author_email='Saurav.Kumar@cognizant.com',
    packages=find_packages(),
    python_requires='>=3.7',
)