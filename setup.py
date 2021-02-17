from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = "Jian's toolbox"
LONG_DESCRIPTION = 'Includes tools that used for tranfering/processing data files and launching twitter monitors.'

# Setting up
setup(
        name="spike", 
        version=VERSION,
        author="Jian Cao",
        author_email="<jccit@caltech.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'google-cloud', 'google-cloud-storage', 'TwitterAPI', 'pandas'],
        keywords=['python', 'toolbox'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS",
            "Operating System :: Ubuntu 18",
        ]
)