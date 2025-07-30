from setuptools import setup, find_packages

setup(
    name="test_simple_math",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],  # No external dependencies for this simple package
    description="A simple math utility package",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/your_username/simple_math",  # Replace with your GitHub repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
