from setuptools import setup, find_packages

setup(
    name="fastapi_simple_app",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "fastapi-app=fastapi_app.app:app",
        ],
    },
    author="Twoje Imię",
    author_email="twoj@email.com",
    description="Prosta aplikacja FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/twojprofil/fastapi_app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    package_data={
        "fastapi_app": ["static/*"],  # Dodaj pliki statyczne
    },

)
