from setuptools import setup, find_packages

setup(
    name="orappgen",
    version="0.1.0",
    description="Générateur d'applications Django structurées (modèles, vues, urls...)",
    author="Ben'Or",
    author_email="benjamin@Djoo.com",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
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
            "startcustomapp=orappgen.starter:main",  # si tu crées une fonction main()
        ],
    },
)
