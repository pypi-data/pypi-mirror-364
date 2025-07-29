import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spatialsurf",
    version="1.3",
    author="Shuyu Liang",
    author_email="",
    description="A self-supervised deep learning method for reference-free deconvolution.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lllsssyyyy/SURF",
    packages=setuptools.find_packages(),
    install_requires=['pandas==1.5.3', 'numpy==1.23.0', 'scanpy==1.9.8', 'scipy==1.9.1',  'rpy2', 'tables', 'seaborn==0.13.2', 'matplotlib==3.7.1'],
    entry_points={
        'console_scripts': [
            'SURF=SURF:main'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)