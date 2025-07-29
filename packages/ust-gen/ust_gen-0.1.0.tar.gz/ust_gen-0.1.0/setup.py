from setuptools import setup, find_packages

setup(
    name="ust_gen",
    version="0.1.0",
    description="User Story Generator plugin from requirements PDF/Excel using Azure OpenAI",
    author="Samuel Rozario",
    author_email="riosam005@gmail.com",
    packages=find_packages(),
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
