# setup.py

from setuptools import setup,find_packages

setup(
    name="Ecode-cmd",
    version="2",
    packages=["Ecode"]+find_packages(),
    entry_points={
        "console_scripts": [
            "Ecode = Ecode.__main__:main",
        ],
    },
    author="AmiraliBatman",
    description="A cool command-line tool with multiple features.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    
    install_requires=[
        "pyttsx3>=2.5",
        "termcolor>=1.1",
        "datetime",
    ],
)
