from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="nnea",       # 包名（PyPI唯一标识，需全小写）
    version="0.1",               # 版本号（每次更新需递增）
    packages=find_packages(),    # 自动包含所有包
    description="A biological inform neural network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chuwei Liu",
    author_email="liuchw26@mail.sysu.edu.cn",
    url="https://github.com/liuchuwei/nnea",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],         # 依赖库列表（如：requests>=2.25）
    python_requires='>=3.6',     # Python版本要求
)