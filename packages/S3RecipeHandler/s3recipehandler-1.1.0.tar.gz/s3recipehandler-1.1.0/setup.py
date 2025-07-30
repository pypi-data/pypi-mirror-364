import pathlib
import setuptools

setuptools.setup(
    name="S3RecipeHandler",
    version="1.1.0",
    author="S4M",
    description="A Custom Skate 3 Recipe File Library",
    long_description=pathlib.Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/l-S4M-l/S3RecipeHandler",
    project_urls={
        "Bug Tracker": "https://github.com/l-S4M-l/S3RecipeHandler/issues",
        "Ko-fi": "https://ko-fi.com/chillsam2",
    },
    license="GPLv3",
    packages=["S3RecipeHandler"],
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)