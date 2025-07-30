from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="custom_app_creator",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Django>=3.0"],
    entry_points={
        'console_scripts': [
            'customapp=django_custom_app_creator.cli:main',
        ],
    },
    description="Un package Django pour créer rapidement des applications personnalisées.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AutoGen",
    author_email="autogen@example.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
    ],
)

