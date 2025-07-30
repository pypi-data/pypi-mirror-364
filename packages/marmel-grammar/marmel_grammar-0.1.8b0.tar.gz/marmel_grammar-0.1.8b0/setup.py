
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marmel-grammar",
    version="0.1.8b",
    author="Dev-Marmel",
    author_email="marmelgpt@gmail.com",
    description="Самая мощная библиотека русской морфологии и транслитерации для Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://t.me/dev_marmel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Russian",
    ],
    python_requires=">=3.8",
    keywords="russian, morphology, declension, grammar, transliteration, names, verbs, linguistic",
    project_urls={
        "Bug Reports": "https://t.me/dev_marmel",
        "Source": "https://t.me/dev_marmel",
        "Documentation": "https://t.me/dev_marmel",
        "Telegram": "https://t.me/dev_marmel",
    },
    install_requires=[],
    extras_require={
        "dev": ["pytest>=6.0", "black", "isort"],
        "telegram": ["python-telegram-bot>=20.0"],
    },
)
