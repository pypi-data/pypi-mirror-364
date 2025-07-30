# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import os
from typing import List

from setuptools import find_packages, setup

# ======================================================================================================================


def get_path_to_this_files_parent_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_path_to_requirements_txt_relative_to_this_file() -> str:
    return os.path.join(get_path_to_this_files_parent_dir(), "requirements.txt")


def load_required_packages_from_requirements_txt() -> List[str]:
    with open(get_path_to_requirements_txt_relative_to_this_file(), "r") as file:
        return [ln.strip() for ln in file.readlines()]


def get_version_number() -> str:
    version_file_path = os.path.join(get_path_to_this_files_parent_dir(), "CODE_VERSION.cfg")
    with open(version_file_path) as version_file:
        version = version_file.read().strip()
    return version


setup(
    # =====
    # Setup
    # =====
    name="libinephany",
    version=get_version_number(),
    description="Inephany library containing code commonly used by multiple subpackages.",
    # =================================
    # Actual packages, data and scripts
    # =================================
    packages=find_packages(),
    package_dir={"libinephany": "libinephany"},
    install_requires=load_required_packages_from_requirements_txt(),
    extras_require={
        "dev": [
            "bump-my-version==0.11.0",
            "black==24.4.2",
            "isort==5.9.3",
            "flake8==7.1.0",
            "pre-commit==4.0.1",
            "mypy==1.13.0",
            "types-PyYAML==6.0.12.20240808",
            "typeguard==4.3.0",
        ]
    },
    python_requires=">=3.6",
)
