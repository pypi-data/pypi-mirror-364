from setuptools import setup, find_packages

setup(
    name="lzl_pytools",
    version="0.2.1",
    author="lzlcodex",
    author_email="yishikong@163.com",
    description="a multi run http req tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/lzlcodex/lzl-pytools.git",
    packages=['lzl_pytools', 'lzl_pytools/apig_sdk', 'lzl_pytools/multi3', 'lms'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # 你的依赖列表
        # "requests>=2.25.1",
    ],
)