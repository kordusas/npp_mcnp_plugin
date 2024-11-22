from setuptools import setup

setup(
    name='npp_mcnp_plugin',
    description="A plugin for Notepad++ that interacts with MCNP",
    author = 'Benjaminas Marcinkevicius',
    version='0.9',
    install_requires=[
        'pytest',
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7"
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",]
)
