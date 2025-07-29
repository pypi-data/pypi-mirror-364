from setuptools import setup, find_packages

setup(
    name='UpgradeDB',
    version='3.0.0',
    description='Banco de dados leve baseado em JSON para Python',
    author='Seu Nome',
    author_email='upgradedb@gmail.com',
    url='https://github.com/???/upgrade_db_py',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
)
