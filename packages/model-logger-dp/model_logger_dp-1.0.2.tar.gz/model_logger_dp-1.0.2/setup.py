import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# you need to change all these
VERSION = '1.0.2'
DESCRIPTION = 'A logger to log the model training, etc.'
LONG_DESCRIPTION = ''

setup(
    name="model_logger_dp",
    version=VERSION,
    author="Ian zhu",
    author_email="IanZhu@m.ldu.edu.cn",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'logger'],
)
