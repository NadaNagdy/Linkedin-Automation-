from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkedin-automation-bot",
    version="1.0.0",
    author="Generic Author",
    author_email="author@example.com",
    description="A modular LinkedIn automation bot for scraping and posting content.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NadaNagdy/automation",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "beautifulsoup4",
        "python-dotenv",
        "openai",
        "lxml", 
    ],
    entry_points={
        'console_scripts': [
            'run-bot=run_bot:main',
        ],
    },
)
