from setuptools import setup

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='keyslide',
    version='0.4',
    entry_points={
        "console_scripts": [
            "keyslide.encrypt = keyslide:cli_encrypt",
            "keyslide.decrypt = keyslide:cli_decrypt"
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)