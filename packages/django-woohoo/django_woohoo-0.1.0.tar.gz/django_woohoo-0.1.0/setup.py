from setuptools import setup, find_packages

setup(
    name="django-woohoo",
    version="0.1.0",
    author="Sarthak Lamba",
    author_email="sarthaksnh5@gmail.com",
    description="Django client for WooHoo gift card API integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sarthaklamba/django-woohoo",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "httpx",
        "dataclasses-json",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
