from setuptools import setup, find_packages

setup(
    name="web_show",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    description="Un package Django simple qui affiche une page HTML",
    author="Ton Nom",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
