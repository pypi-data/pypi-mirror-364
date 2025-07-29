from setuptools import setup

setup(
    name='opsicos',
    version='1.1.2',  # Version bump
    author='Tawsif',
    description='A professional Python SDK for the Opsicos AI Gateway.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=['opsicos'],  # The corrected, explicit package declaration
    install_requires=['requests'],
    python_requires='>=3.6',
)