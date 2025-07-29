from setuptools import setup, find_packages

setup(
    name="vasuSTT",
    version="0.1",
    author="vasu",
    author_email="vasu@example.com",
    description="This is STT created by Vasu",
    packages=find_packages(),  # Don't need to also list manually
    install_requires=[
        "selenium",
        "webdriver-manager"
    ],
)
