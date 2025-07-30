from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="authservice-django",
    version='1.0.0',
    author="hasnain3033",
    author_email="hasnain3033@gmail.com",
    description="Django SDK for Auth Service - Authentication and authorization for Django applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hasnain3033/django-auth-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
    python_requires=">=3.8",
    install_requires=[
        "django>=3.2",
        "requests>=2.28.0",
        "pyjwt>=2.8.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "drf": ["djangorestframework>=3.12.0"],
        "async": ["httpx>=0.24.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-django>=4.5.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "django-stubs>=4.2.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/hasnain3033/django-auth-sdk/issues",
        "Source": "https://github.com/hasnain3033/django-auth-sdk",
        "Documentation": "https://github.com/hasnain3033/django-auth-sdk#readme",
    },
)