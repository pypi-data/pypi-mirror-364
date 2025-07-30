from setuptools import setup, find_packages

setup(
    name='Packages_special',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Un package de base Django',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='NDA',
    author_email='angecedricnda6@gmail.com',
    install_requires=[
        'django>=3.2',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
