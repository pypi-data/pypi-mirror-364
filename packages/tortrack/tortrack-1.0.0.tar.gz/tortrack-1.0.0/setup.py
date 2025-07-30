from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tortrack",
    version="1.0.0",
    author="Mohammad Hossein Norouzi",
    author_email="hosein.norozi434@gmail.com",
    description="Simple Telegram bot for downloading music with Tor anonymity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohammadHNdev/tortrack",
    packages=find_packages(),
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
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Internet :: Proxy Servers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiogram>=3.0.0",
        "spotipy>=2.22.0",
        "yt-dlp>=2023.7.6",
        "pymongo>=4.0.0",
        "motor>=3.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "PySocks>=1.7.1",
        "stem>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "tortrack=tortrack.cli:main",
        ],
    },
    keywords="telegram bot music download spotify tor anonymous",
    project_urls={
        "Bug Reports": "https://github.com/MohammadHNdev/tortrack/issues",
        "Source": "https://github.com/MohammadHNdev/tortrack",
    },
    include_package_data=True,
    zip_safe=False,
)