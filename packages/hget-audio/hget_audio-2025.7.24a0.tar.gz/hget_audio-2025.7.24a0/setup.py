from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hget_audio',
    version='2025.7.24a',
    description='Comprehensive audio scraping tool for websites.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='huang yi yi',
    author_email='363766687@qq.com',
    url="https://github.com/hyy-PROG/hget_audio",
    packages=find_packages(),
    package_dir={'hget_audio': 'hget_audio'},
    package_data={"hget_audio": ["**"]},
    include_package_data=True,
    install_requires=[
        "scrapy>=2.5.0",
        "beautifulsoup4>=4.9.3",
        "tldextract>=3.1.0",
        "python-magic>=0.4.24",
        "pydub>=0.25.1",
        "requests>=2.25.1",
        "setuptools>=54.1.2",
    ],
    entry_points={
        'console_scripts': [
            'hget-audio = hget_audio.commands.crawl:Command.run',
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
    keywords="audio scraping downloader web crawler mp3 wav ogg podcast",
    project_urls={
        "Bug Tracker": "https://github.com/hyy-PROG/hget_audio/issues",
        "Documentation": "https://github.com/hyy-PROG/hget_audio/wiki",
        "Source Code": "https://github.com/hyy-PROG/hget_audio",
    },
    license="MIT",
)