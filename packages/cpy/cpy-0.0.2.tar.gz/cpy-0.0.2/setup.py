from setuptools import setup, find_packages

setup(
    name="cpy",
    version="0.0.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "setuptools>=70.3.0",
        "deprecated",
    ],
    entry_points={
        'console_scripts': [
            'ccrypt = cpy.ccrypt.cli:main',
        ],
    },
    author="CHARZ",
    author_email="your.email@example.com",
    description="Charz Python Library",
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
