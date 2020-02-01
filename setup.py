import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sparcli",
    version="0.0.1",
    author="Alex Fraser",
    author_email="alex.d.fraser@gmail.com",
    description="Display dynamic metrics as text (sparklines)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/z0u/sparcli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
