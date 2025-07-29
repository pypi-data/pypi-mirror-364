from setuptools import setup, find_packages

with open("README_pypi.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mesh_generator",
    version="1.1.10",
    author="Predictive Science Inc",
    author_email="oissan@predsci.com",
    description="Python subroutines to create a 1D mesh in Python.",
    keywords=['Mesh Generation', 'Grid'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/predsci/mesh_generator",
    packages=find_packages(include=['mesh_generator', 'mesh_generator.src', 'mesh_generator.bin', 'mesh_generator.ui',
                                    'mesh_generator.hdf']),
    include_package_data=True,
    install_requires=['numpy>=1.15.2', 'matplotlib>=3.0.0', 'scipy >= 1.1.0', 'pyhdf>=0.9.10', 'h5py>=2.8.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires='>=3.5',
)
