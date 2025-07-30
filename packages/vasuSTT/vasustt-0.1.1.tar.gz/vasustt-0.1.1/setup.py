from setuptools import setup, find_packages

setup(
    name='vasuSTT',                  # Change as needed
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'speechrecognition',
        'selenium',
    ],
    author='Vasu',
    description='A simple STT module for JARVIS',
    long_description='A longer description of your vasuSTT speech recognition system.',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
