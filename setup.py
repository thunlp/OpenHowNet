import setuptools

VERSION = "test"
with open("OpenHowNet/version.py", "r") as fver:
    VERSION = fver.read().replace("VERSION", "").replace("=", "").replace("\"", "").strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = '<h1 align="center">OpenHowNet</h1>\n'+fh.read().split('### [中文版本](README_ZH.md)\n\n')[1]

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
    install_requires=['anytree==2.4.3','requests==2.22.0','tqdm==4.31.1'],
    python_requires=">=3.6"
)
