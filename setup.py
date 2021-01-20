from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = "Jian's toolbox"
LONG_DESCRIPTION = 'Includes tools that used for tranfering/processing data files'

# Setting up
setup(
        name="spike", 
        version=VERSION,
        author="Jian Cao",
        author_email="<jccit@caltech.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'google-cloud-storage'],
        keywords=['python', 'toolbox'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)