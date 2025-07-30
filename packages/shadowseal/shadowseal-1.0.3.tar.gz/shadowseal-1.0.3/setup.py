from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

extensions = [
    Extension("runner.cy_loader", ["runner/cy_loader.pyx"])
]

setup(
    name="shadowseal",
    version="1.0.3",
    description="Secure Python encryption and execution framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Monarch of Shadows",
    author_email="farhanbd637@gmail.com",
    url="https://github.com/AFTeam-Owner/shadowseal",
    packages=find_packages(),
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
    },
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    entry_points={
        "console_scripts": ["shadowseal=shadowseal.cli:main"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
    keywords='encryption, obfuscation, security, python, anti-debugging',
)
