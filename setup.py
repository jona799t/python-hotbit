from setuptools import setup, find_packages
from pathlib import Path

VERSION = '0.1.0'
DESCRIPTION = "A Python package for the cryptocurrency exchange Hotbit that doesn't require an API Key, making it available to everyone"
long_description = (Path(__file__).parent / "readme.md").read_text()

# Setting up
setup(
    name="hotbit",
    version=VERSION,
    author="jona799t",
    #author_email="<not@available.com>",
    url = 'https://github.com/jona799t/python-hotbit',
    description=DESCRIPTION,
    long_description=long_description,
    license_files = ('LICENSE.txt',),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=["pycryptodome", "anticaptchaofficial", "twocaptcha", "2captcha-python", "requests", "requestsWS", "undetected-chromedriver"],
    keywords=['hotbit', 'api', 'crypto', 'exchange'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
