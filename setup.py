from setuptools import setup, find_packages
import os

long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="Grok3API",
    version="0.0.1.dev4",
    author="boykopovar",
    author_email="boykopovar@gmail.com",
    description="Python-библиотека для взаимодействия с Grok3 в стиле OpenAI. "
                "Автоматически получает cookies, поэтому их не обязательно указывать вручную. "
                "A Python library for interacting with Grok3 in the style of OpenAI. "
                "Automatically retrieves cookies, so specifying them manually is not required.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boykopovar/Grok3API",
    # install_requires=[
    #     "undetected-chromedriver==3.5.5"
    # ],
    packages=find_packages(include=["grok3", "grok3.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
