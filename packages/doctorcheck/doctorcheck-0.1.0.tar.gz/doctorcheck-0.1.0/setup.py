from setuptools import setup, find_packages

setup(
    name="doctorcheck",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.2",  # ou la version que tu cibles
    ],
    description="A reusable Django app for health check logic.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Keita",
    author_email="ton@email.com",
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
