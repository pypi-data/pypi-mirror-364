from setuptools import setup, find_packages

setup(
    name="ust_gen",
    version="0.2.1",
    description="User Story Generator plugin from requirements PDF/Excel using Azure OpenAI",
    author="Samuel Rozario",
    author_email="riosam005@gmail.com",
    packages=find_packages(include=["ust_gen", "ust_gen.*"]),
    install_requires=[
        "openai",
        "PyPDF2",
        "pandas",
        "openpyxl",
        "python-dotenv"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
