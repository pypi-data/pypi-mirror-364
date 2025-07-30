from setuptools import setup, find_packages

setup(
    name="text_outputter",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["python-docx"],
    entry_points={
        'console_scripts': [
            'output=text_outputter.cli:main',
        ],
    },
    author="Your Name",
    author_email="your_email@example.com",
    description="一个简单的命令行文本输出工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords=["text", "output", "cli", "tool"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

