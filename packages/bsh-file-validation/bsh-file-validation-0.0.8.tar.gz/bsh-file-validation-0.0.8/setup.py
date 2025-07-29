from setuptools import setup, find_packages

setup(
    name="bsh-file-validation",
    version="0.0.8",
    packages=find_packages(),
    install_requires=["msal==1.32.3", "tinytag==2.1.0", "moviepy==1.0.3"],
    author="BSH_USER",
    author_email="ramvinoth1993@gmail.com",
    description="A simple library for file validation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/bsh-file-validation/",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)