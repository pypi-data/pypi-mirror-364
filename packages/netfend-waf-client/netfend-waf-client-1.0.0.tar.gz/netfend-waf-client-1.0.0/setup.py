from setuptools import setup, find_packages

setup(
    name="netfend-waf-client",
    version="1.0.0",
    description="WAF Client SDK for Python - Netfend",
    author="Seu Nome",
    author_email="support@netfend.emailsbit.com",
    url="https://github.com/Shieldhaus/netfend-waf-client",
    packages=find_packages(),
    install_requires=[
        "requests",
        "aiohttp",
        "flask",
        "fastapi",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
