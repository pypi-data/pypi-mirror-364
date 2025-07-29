from setuptools import setup, find_packages

setup(
    name="saksin-vect2",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    author="Ravi Kishan",
    author_email="your.email@example.com",  # Replace with your actual email
    description="Python SDK for querying Saksin AI chunked retrieval API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kishanravi887321/saksin-vect2.git",
  
    python_requires='>=3.6',
)
