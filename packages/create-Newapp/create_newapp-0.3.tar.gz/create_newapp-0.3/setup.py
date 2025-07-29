from setuptools import setup, find_packages

setup(
    name="create_Newapp",
    version="0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "create-django=create_django.__main__:main"
        ]
    },
    author="Tieba",
    description="Un outil pour créer une application Django complète automatiquement.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ],
    python_requires='>=3.6',
)
