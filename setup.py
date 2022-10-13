from setuptools import setup

setup(
    name='PyForks',
    version='0.0.2',
    author='Trailforks Python Library',
    author_email='MinnMTB@gmail.com',
    packages=['PyForks', 'PyForks.test'],
    #scripts=['bin/script1','bin/script2'],
     project_urls={  # Optional
        "Bug Reports": "https://github.com/cribdragg3r/PyForks/issues",
        "Funding": "https://donate.pypi.org",
        "Source": "https://github.com/cribdragg3r/PyForks",
    },
    url='http://pypi.python.org/pypi/PyForks/',
    license='LICENSE.txt',
    description='A package to interface with Trailforks.com',
    long_description=open('README.txt').read(),
    install_requires=[
        "pytest",
        "tqdm",
        "requests",
        "pandas",
        "lxml",
        "bs4",
        "html5lib",
    ],
)