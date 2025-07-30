from setuptools import setup, find_packages

version = {}
with open("__version__.py") as f:
    exec(f.read(), version)

setup(
    name="xwarning",
    version=version["version"],
    author="Hadi Cahyadi",
    description="Enhanced warning output using Rich with icons and colors.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cumulus13/xwarning",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rich>=13.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
