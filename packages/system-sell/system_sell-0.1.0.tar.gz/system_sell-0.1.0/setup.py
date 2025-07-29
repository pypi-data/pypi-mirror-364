from setuptools import setup, find_packages

setup(
    name="system-sell",
    version="0.1.0",
    description="Secure P2P File Sharing Tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ayushkiller",
    author_email="your.email@example.com",
    url="https://github.com/Ayushkiller/System-sell",
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"": "."},
    install_requires=[
        "cryptography",
        "qrcode[pil]"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "system-sell=system_sell:main"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
