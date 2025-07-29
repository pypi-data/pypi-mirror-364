from setuptools import setup, find_packages

setup(
    name="DoctorCheck",
    version="0.4.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.0",
    ],
    entry_points={
        "console_scripts": [
            "create_doctorcheck = create_doctorcheck:main",
        ]
    },
    author="Votre Nom",
    author_email="keitamohamed1432@gmail.com",
    description="Un package Django pour évaluer la santé basée sur la tension artérielle sans base de données",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)