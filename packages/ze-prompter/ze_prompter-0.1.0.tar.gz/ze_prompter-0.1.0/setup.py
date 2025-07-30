from setuptools import setup, find_packages
import os

def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A library for managing prompt templates with versioning"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="ze-prompter",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'ze_prompter': [
            'dashboard/templates/*.html',
            'dashboard/templates/**/*.html',
        ],
    },
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'ze-prompter=ze_prompter.cli:cli',
            'zeprompter=ze_prompter.cli:cli',
        ],
    },
    scripts=['run_server.py'],
    author="Olsi Hoxha",
    author_email="olsihoxha824@gmail.com",
    description="A library for managing prompt templates with versioning and AI models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/olsihoxha/zeprompter",
    project_urls={
        "Bug Reports": "https://github.com/olsihoxha/zeprompter/issues",
        "Source": "https://github.com/olsihoxha/zeprompter",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="prompt templates, ai, machine learning, versioning, fastapi, web interface",
    zip_safe=False,
)