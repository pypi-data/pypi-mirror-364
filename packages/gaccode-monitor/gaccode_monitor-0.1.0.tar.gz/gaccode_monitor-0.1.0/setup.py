from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gaccode-monitor",
    version="0.1.0",
    author="GACCode Monitor Team",
    author_email="yourname@example.com",
    description="A system tray application to monitor GACCode credits balance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/watchGacCredits",
    packages=["py", "py.utils"],
    package_dir={"": "src"},
    package_data={
        "py": ["*.py"],
        "py.utils": ["*.py"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "schedule",
        "pystray",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "gaccode-monitor=py.gaccode_tray_icon:setup_tray",
            "gaccode-logger=py.fetch_gaccode_balance:main",
        ],
    },
) 