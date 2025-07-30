from setuptools import setup, find_packages

setup(
    name="quipy",
    version="0.1.0",
    author="MrYuGoui",
    author_email="MrYuGoui@163.com",
    description="一些常用工具",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mryugoui/quipy",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy"
    ],
)
