import os
import shutil
import sys
from setuptools import setup, find_packages

version = None

with open("tranci/__init__.py", "r") as f:
    for line in f.readlines():
        if line.startswith("__version__"):
            version = line.split("=", 1)[1].strip().replace('"', "")

if version is None:
    print("where's the version?!?!??!!")
    sys.exit(1)

print(f"version {version}")

with open("README.md", "r") as f:
    long_description = f.read()

current_dir_mess = os.listdir(".")

if any(
    (
        "dist" in current_dir_mess,
        "tranci.egg-info" in current_dir_mess,
        "build" in current_dir_mess,
    )
):
    print("cleaning up your previous mess...")

    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("tranci.egg-info", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)

    print("done!")

setup(
    name="tranci",
    version=version,
    description="Tranci: a no-dependencies, lightweight, easy-to-use ANSI library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Butterroach",
    author_email="butterroach@outlook.com",
    url="https://github.com/Butterroach/tranci",
    license="LGPLv3+",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    project_urls={
        "Source": "https://github.com/Butterroach/tranci",
        "Bug Tracker": "https://github.com/Butterroach/tranci/issues",
    },
    include_package_data=True,
    package_data={
        'package': ['py.typed'],
    },
)
