from setuptools import setup, find_packages

setup(
    name="saksin_vect2",
    version="0.1.6",
    packages=find_packages(),
    install_requires=["requests"],
    author="Ravi Kishan",
    author_email="kishanravi887321@gmail.com", 
     package_dir={'': 'saksin_vect2'},
    description="Python SDK for querying Saksin AI chunked retrieval API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kishanravi887321/saksin-vect2.git",
  
    python_requires='>=3.6',
)



