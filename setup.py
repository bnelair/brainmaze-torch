# Copyright 2020-present, Mayo Clinic Department of Neurology
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""Minimal setup.py shim for legacy tooling.

Primary metadata and dependencies live in pyproject.toml.
This file exists so older pip/setuptools workflows that still
invoke setup.py continue to work.
"""

import setuptools
from pathlib import Path

# Try to obtain the version from brainmaze_torch._version without requiring
# setuptools_scm. This avoids importing the whole package when possible.
_version = "0.0.0"
try:
    # preferred: import the module attribute
    from importlib import import_module
    _version = import_module("brainmaze_torch._version").__version__
except Exception:
    try:
        # fallback: read and exec the _version.py file directly
        version_file = Path(__file__).resolve().parent / "brainmaze_torch" / "_version.py"
        about = {}
        about_text = version_file.read_text(encoding="utf-8")
        exec(about_text, about)
        _version = about.get("__version__", _version)
    except Exception:
        # leave default version if everything fails
        pass

setuptools.setup(
    name="brainmaze-torch",
    version=_version,
    # no use_scm_version / no setuptools_scm required
    description="BrainMaze: Brain Electrophysiology, Behavior and Dynamics Analysis Toolbox - Torch",
    author="Filip Mivalt",
    author_email="mivalt.filip@mayo.edu",
    url="https://github.com/bnelair/brainmaze_torch",
    license="BSD-3-Clause",

    packages=setuptools.find_packages(exclude=["tests*", "examples*", "docs*", "docs_src*"]),
    include_package_data=True,
    package_data={
        "brainmaze_torch": ["seizure_detection/_models/*.pt"]
    },

    classifiers=[
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
    ],

    # Dependencies and full metadata are declared in pyproject.toml.
    install_requires=[],
    python_requires=">=3.9.0",
)
