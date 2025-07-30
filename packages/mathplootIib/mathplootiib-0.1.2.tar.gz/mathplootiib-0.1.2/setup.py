from setuptools import setup, find_packages

setup(
    name='mathplootIib',  # your package name
    version='0.1.2',
    description='hi',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ayush Chadha',
    author_email='elegantShock3307@gmail.com',
    url='https://github.com/elegantShock2258/mathplotlib',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
