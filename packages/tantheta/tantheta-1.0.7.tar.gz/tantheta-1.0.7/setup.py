import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""

setup(
    name="tantheta",  
    version="1.0.7",  
    author="Ayush Parwal",
    author_email="ayushparwal777@gmail.com",  
    description="An intuitive symbolic math library for algebra, calculus, trigonometry, and beyond.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ayushparwal/tantheta",  
    include_package_data=True,
    install_requires=[
        "sympy>=1.12",  
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
