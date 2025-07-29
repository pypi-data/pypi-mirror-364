from setuptools import find_packages
from setuptools import setup
from Telegrams import appname
from Telegrams import version
from Telegrams import install
from Telegrams import caption
from Telegrams import pythons
from Telegrams import clinton
from Telegrams import profile
from Telegrams import mention
from Telegrams import DATA01
from Telegrams import DATA02

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
