from setuptools import setup, find_packages

setup(
    name="orappgen",
    version="0.1.1",
    description="Générateur d'applications Django structurées (modèles, vues, urls...)",
    author="Ben'Or",
    author_email="benjamin@Djoo.com",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",

    install_requires=[
        "Django>=3.2",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "startcustomapp=orappgen.starter:main",  #fonction main()
        ],
    },

)
