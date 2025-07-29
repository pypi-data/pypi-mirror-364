from setuptools import setup, find_packages

setup(
    name="pseudogenero234",
    version="1.1.5",
    author="Monique",
    author_email="mreineboto@gmail.com",
    description="Package pour générer des pseudonymes d'étudiants fictifs",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Faker>=18.0.0"
    ],
    entry_points={
        'console_scripts': [
            'enregistrement=enregistreùent.cli:main',
        ],
    },
)
