import platform
from setuptools import setup, find_packages


try:
    with open("README.md",encoding="utf-8",mode="r") as f:
        long_desc=f.read()
except:
    long_desc=""

setup(
    name="python3-log",
    version="0.0.11",
    description="used to print log for any app or platform",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="redrose2100",
    author_email="hitredrose@163.com",
    maintainer="redrose2100",
    maintainer_email="hitredrose@163.com",
    url="https://gitee.com/devops_dev/log",
    project_urls={
        "Documentation": "https://gitee.com/devops_dev/log/README.md"
    },
    license="MIT",
    install_requires =[
        "concurrent_log_handler"
    ],
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
        ],
    },
    data_files=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ]
)