from setuptools import setup, find_packages

setup(
    name="BlazeCache",
    version='0.1.0',
    packages=find_packages(where="src"),
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',  
    package_dir={"": "src"},
    install_requires=[
        "semver",  
    ],
    classifiers=[
        'Programming Language :: Python :: 3',  # 支持 Python 3
        'License :: OSI Approved :: MIT License',  # MIT 许可证
        'Operating System :: OS Independent',  # 支持跨平台

    ]
)
