
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marmel-grammar",
    version="0.1.8",
    author="Dev-Marmel",
    author_email="marmelgpt@gmail.com",
    description="Самая мощная библиотека русской морфологии и транслитерации для Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dev-marmel/marmel-grammar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: Russian",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0; python_version<'3.9'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "telegram": [
            "python-telegram-bot>=20.0",
        ],
        "web": [
            "flask>=2.0",
            "fastapi>=0.100",
        ],
    },
    entry_points={
        "console_scripts": [
            "marmel-grammar=main:main",
        ],
    },
    keywords=[
        "russian", "morphology", "transliteration", "grammar", "nlp",
        "language-processing", "declension", "conjugation", "russian-language",
        "text-processing", "linguistics", "telegram-bot", "names"
    ],
    project_urls={
        "Bug Reports": "https://github.com/dev-marmel/marmel-grammar/issues",
        "Source": "https://github.com/dev-marmel/marmel-grammar",
        "Telegram": "https://t.me/dev_marmel",
    },
    include_package_data=True,
    package_data={
        "marmel_grammar": ["*.py", "dataset.py"],
    },
    zip_safe=False,
)
