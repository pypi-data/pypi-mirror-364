from setuptools import setup, find_packages

setup(
    name="django-polls-natacha",
    version="0.1.0",
    description="A reusable Django app for polls",
    author="nandja matacha",
    author_email="nandjakessianatacha@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
    ],
)
