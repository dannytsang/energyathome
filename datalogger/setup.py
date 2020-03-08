import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="energyathome",
    version="0.7.4",
    author="Danny Tsang",
    author_email="danny@dannytsang.co.uk",
    description="Data logging from a CurrentCost device",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dannytsang/energyathome",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: General Public License v3 (GPLv3)",
        "Operating System :: Unix"
    ],
    python_requires='>=2.6',
)
