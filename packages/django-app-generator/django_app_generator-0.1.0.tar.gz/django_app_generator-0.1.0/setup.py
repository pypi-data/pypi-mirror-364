from setuptools import setup, find_packages

setup(
    name="django-app-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "django-create-app=django_app_generator.create_app:main",
        ],
    },
    author="Nicosidick",
    author_email="abou210traore@gmail.com",
    description="Un outil pour créer des applications Django similaires à django-admin startapp",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/votre-repo/django-app-generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)