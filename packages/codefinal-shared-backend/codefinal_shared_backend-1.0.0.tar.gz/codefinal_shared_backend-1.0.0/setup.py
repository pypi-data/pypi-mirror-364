from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codefinal-shared-backend",
    version="1.0.0",
    author="CodeFinal Team",
    author_email="team@codefinal.com",
    description="Shared backend utilities for CodeFinal products",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeFinal/codefinal/tree/feature/COD-141-shared-component-library/packages/backend-utils",
    project_urls={
        "Bug Tracker": "https://github.com/CodeFinal/codefinal/issues",
        "Repository": "https://github.com/CodeFinal/codefinal/tree/feature/COD-141-shared-component-library",
        "Documentation": "https://github.com/CodeFinal/codefinal/tree/feature/COD-141-shared-component-library/packages/backend-utils#readme",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.0.0",
        "djangorestframework>=3.14.0",
        "django-tenants>=3.0.0",
        "pyotp>=2.6.0",
        "python-decouple>=3.6",
        "cryptography>=3.4.8",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-django>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="django authentication shared utilities backend api",
    include_package_data=True,
    zip_safe=False,
) 