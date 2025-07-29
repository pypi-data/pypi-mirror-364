from setuptools import setup, find_packages

setup(
    name='opsicos',
    version='1.1.1',
    author='Tawsif',
    description='A professional Python SDK for the Opsicos AI Gateway.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['requests'],
    python_requires='>=3.6',
)
