from setuptools import setup, find_packages

setup(
    name="reverseword_TIB",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "reverseword=reverseword.__main__:main"
        ]
    },
    description="Un petit outil pour renverser un mot.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Tieba",
    author_email="meitetieba@gmail.com.com",
    url="https://pypi.org/project/reverseword/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
