from setuptools import setup, find_packages

setup(
    name="charchecker",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="Une app Django pour vérifier le type d’un caractère.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tonpseudo/charchecker",
    author="David GBONGUE",
    author_email="davidmade92@gmail.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
