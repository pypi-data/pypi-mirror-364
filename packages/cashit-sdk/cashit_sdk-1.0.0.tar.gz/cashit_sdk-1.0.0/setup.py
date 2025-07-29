from setuptools import setup, find_packages

setup(
    name="cashit_sdk",
    version="1.0.0",
    description="Python SDK for CashIt cheque APIs",
    author="Tekku",
    packages=find_packages(),
    install_requires=["requests", "cloudinary"],
)
