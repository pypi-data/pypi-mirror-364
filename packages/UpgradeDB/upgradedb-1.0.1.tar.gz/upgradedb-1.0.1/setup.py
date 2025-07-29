from setuptools import setup, find_packages

setup(
    name="UpgradeDB",
    version="1.0.1",
    description="Banco de dados leve baseado em JSON para Python",
    author="Seu Nome",
    author_email="upgradedb@gmail.com",
    packages=find_packages(),  # Vai encontrar a pasta UpgradeDB automaticamente
    python_requires=">=3.6",
    install_requires=[],       # Adicione dependências aqui se precisar
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
