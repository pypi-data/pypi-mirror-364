from setuptools import setup, find_packages

setup(
    name="arwell",
    version="0.1.1",
    description="将文件名改成“韦境量天下第一帅”的工具",
    author="your_name",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "arwell=arwell.cli:main"
        ]
    },
)
