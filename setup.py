import os

from setuptools import setup
from setuptools.extension import Extension


ext_modules = [
    Extension(
        "caterpillar._core",
        [os.path.join("caterpillar", "_core.c")],
        extra_compile_args=["-O3", "-g", "-UNDEBUG"],
        extra_link_args=[],
    ),
]

crypto_deps = ["cryptography"]
compression_deps = ["lzallright"]
dev_deps = [
    "pytest",
    "black",
    "isort",
    "sphinx",
    "pydata-sphinx-theme",
    "sphinx-design",
]
all_deps = crypto_deps + compression_deps + dev_deps

optional_dependencies = {
    "crypto": crypto_deps,
    "compression": compression_deps,
    "all": all_deps,
    "dev": dev_deps,
}

setup(
    name="caterpillar",
    version="0.1.1",
    description="Library to pack and unpack structurized binary data.",
    maintainer="MatrixEditor",
    maintainer_email="not@supported.com",
    url="https://github.com/MatrixEditor/caterpillar",
    project_urls={
        "Documentation": "https://matrixeditor.github.io/caterpillar",
        "Source": "https://github.com/MatrixEditor/caterpillar",
    },
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    extras=optional_dependencies,
    license="GNU General Public License",
    ext_modules=ext_modules,
    packages=["caterpillar"],
    package_data={"caterpillar": ["py.typed", "*.pyi"]},
    long_description=(
        open("README.md", encoding="utf-8").read()
        if os.path.isfile("README.md")
        else ""
    ),
    long_description_content_type="text/markdown",
    zip_safe=False,
    python_requires=">=3.12",
)
