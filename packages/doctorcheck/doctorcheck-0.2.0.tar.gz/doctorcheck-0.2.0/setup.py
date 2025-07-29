from setuptools import setup, find_packages

setup(
    name="doctorcheck",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.2",
    ],
    description="A reusable Django app for health check logic.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Keita",
    author_email="ton@email.com",
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
