from setuptools import find_packages
from setuptools import setup
from Telegramd import appname
from Telegramd import version
from Telegramd import install
from Telegramd import caption
from Telegramd import pythons
from Telegramd import clinton
from Telegramd import profile
from Telegramd import mention
from Telegramd import DATA01
from Telegramd import DATA02

with open("README.md", "r") as o:
    description = o.read()
    
setup(
    url=profile,
    name=appname,
    author=clinton,
    version=version,
    keywords=mention,
    classifiers=DATA02,
    author_email=DATA01,
    description=caption,
    python_requires=pythons,
    packages=find_packages(),
    install_requires=install,
    long_description=description,
    long_description_content_type="text/markdown")
