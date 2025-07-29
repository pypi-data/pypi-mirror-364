from setuptools import setup, find_packages

# Function to parse the requirements file
def parse_requirements(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="inbox4us_pos_printer",
    setup_requires=["setuptools_scm"],
    use_scm_version={"write_to": "pos_printer/_version.py"},
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    author="Daniel",
    description="A brief description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/repository",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
