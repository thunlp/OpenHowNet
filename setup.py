import setuptools

VERSION = "test"
with open("OpenHowNet/version.py", "r") as fver:
    VERSION = fver.read().replace("VERSION", "").replace(
        "=", "").replace("\"", "").strip()

long_description = "OpenHowNet API is developed by [THUNLP](http://thunlp.org/), which provides a convenient way to search information in HowNet, display sememe trees, calculate word similarity via sememes, etc. You can also visit our [website](https://openhownet.thunlp.org) to enjoy searching and exhibiting sememes of words online."

setuptools.setup(
    name="OpenHowNet",
    version=VERSION,
    author="THUNLP",
    author_email="thunlp@gmail.com",
    description="OpenHowNet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thunlp/OpenHowNet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'anytree',
        'setuptools',
        'tqdm',
        'requests',
    ],
    python_requires=">=3.6"
)
