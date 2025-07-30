from setuptools import setup, find_packages

setup(
    name="bennett",
    version="0.1.1",
    description="A simple wrapper to query Groq's LLaMA-3 models using streaming",
    author="Harrison Bennett J",
    author_email="harrisonbennett30@gmail.com",
    packages=find_packages(),
    install_requires=["groq", "python-dotenv"],
    python_requires=">=3.7",
)
