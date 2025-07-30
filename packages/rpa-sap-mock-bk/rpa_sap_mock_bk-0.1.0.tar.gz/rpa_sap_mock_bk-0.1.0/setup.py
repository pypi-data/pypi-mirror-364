from setuptools import setup, find_packages

setup(
    name='rpa-sap-mock-bk',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'robotframework==6.1.1',
        'requests'
        'robotframework-pythonlibcore>=4.0'
    ],
    author='Minh Chiến',
    description='Robot Framework library for SAP Cloud SDK APIs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/chiencse/rpa-sap',
    classifiers=[
        'Framework :: Robot Framework',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)