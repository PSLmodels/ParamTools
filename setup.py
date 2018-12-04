import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="paramtools",
    version="0.0.2",
    author="Hank Doupe",
    author_email="henrymdoupe@gmail.com",
    description="Library for parameter processing and validation with a focus on computational modeling projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hdoupe/ParamTools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
