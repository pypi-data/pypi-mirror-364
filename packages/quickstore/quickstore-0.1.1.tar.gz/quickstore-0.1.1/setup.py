from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quickstore",
    version="0.1.1",
    description="A developer-friendly, zero-dependency key-value database with TTL, file management, and in-memory search.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Avishek Devnath",
    author_email="avishekdevnath@gmail.com",
    url="https://github.com/yourusername/quickstore",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'quickstore=quickstore.cli_entry:main',
        ],
    },
    python_requires='>=3.6',
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 