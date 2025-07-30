from setuptools import setup, find_packages

setup(
    name="arwell",
    version="0.1.2",
    description="将文件名改成“韦境量天下第一帅”的工具",
    author="29Thmarch",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "arwell=arwell.cli:main"
        ]
    },
)
