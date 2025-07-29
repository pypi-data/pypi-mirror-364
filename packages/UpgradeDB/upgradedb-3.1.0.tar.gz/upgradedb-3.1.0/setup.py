from setuptools import setup, find_packages

setup(
    name="UpgradeDB",
    version="3.1.0",
    author="Seu Nome",
    author_email="upgradedb@gmail.com",
    description="Banco de dados leve baseado em JSON para Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seuusuario/upgrade_db_py",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        
    ],
)
