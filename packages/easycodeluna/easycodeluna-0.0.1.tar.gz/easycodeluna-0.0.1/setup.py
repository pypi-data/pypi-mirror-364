
from setuptools import setup, find_packages

setup(
    name='easycodeluna',
    version='0.0.1',
    packages=find_packages(),
    description='Pacote educativo com funções básicas de Python',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Aparecido Roberto Luna',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Education',
        'Topic :: Education',
    ],
    python_requires='>=3.6',
)
