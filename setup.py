from setuptools import setup, find_packages

setup(
    name="asyncioList",
    version="1.0",
    author="303_SeeOther",
    author_email="l.z.cheng.1106@gmail.com",
    description="An asynchronous list implementation with concurrency control",
    long_description=open("README.md", "r", encoding="utf-8").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/303-SeeOther/asyncioList",
    packages=find_packages(),
    install_requires=[],
    keywords=["asyncio", "list", "concurrency"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)