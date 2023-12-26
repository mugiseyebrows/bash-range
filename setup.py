from setuptools import setup, find_packages

with open('readme.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    packages = find_packages(),
    name = 'bashrange',
    version='0.0.4',
    author="Stanislav Doronin",
    author_email="mugisbrows@gmail.com",
    url='https://github.com/mugiseyebrows/bash-range',
    description="Bash range expression evaluator for your cli application",
    long_description = long_description,
    install_requires = []
)