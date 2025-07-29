from setuptools import setup, find_packages

setup(
    name="django-compteurvues",
    version="0.1.0",
    description="Package Django pour compter les vues sur n'importe quel objet comme une page, un article de blog, un produit etc.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author="martial",
    author_email="martil0@egmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
