import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hks_lib-huykingsofm", # Replace with your own username
    version="0.0.1",
    author="huykingsofm",
    author_email="huykingsofm@gmail.com",
    description="A python utility library is written by huykingsofm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huykingsofm/hks_lib",
    project_urls={
        "Bug Tracker": "https://github.com/huykingsofm/hks_lib/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7.1",
    install_requires=["cryptography"],
    setup_requires=["pytest-runner==4.4"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)