from setuptools import setup, find_packages

setup(
    name='ezpath',
    version='1.7',
    packages=find_packages(),
    description='Turn-Key solution to manage paths relative to the current file',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Vittorio Pascucci',
    py_modules=['ezpath'],
    python_requires='>=3.6',
    install_requires=[],
)


# run the following:
# pip install build
# pip install twine
# pip install poetry-core
# python3 -m build
# twine upload dist/*
