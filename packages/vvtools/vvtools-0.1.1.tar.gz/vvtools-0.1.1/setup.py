from setuptools import setup, find_packages

setup(
    name="vvtools",
    version="0.1.1",
    description="파이썬 개인 유틸리티",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Andy Cho",
    author_email="soohwancho@korea.ac.kr",
    url="https://github.com/splendidz/vvtools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
