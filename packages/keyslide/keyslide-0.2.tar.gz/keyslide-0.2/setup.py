from setuptools import setup, find_packages

setup(
    name='keyslide',
    version='0.2',
    entry_points={
        "console_scripts": [
            "keyslide.encrypt = keyslide:cli_encrypt"
        ],
    }
)