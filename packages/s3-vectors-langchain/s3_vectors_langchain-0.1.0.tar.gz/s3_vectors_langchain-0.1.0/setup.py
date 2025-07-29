from setuptools import setup, find_packages

setup(
    name="s3-vectors-langchain",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "langchain",
        "botocore",
    ],
    author="Swagata Roy",
    author_email="r.swagata98@gmail.com",
    description="LangChain VectorStore implementation using AWS S3 Vectors",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/s3-vectors-langchain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)