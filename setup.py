from setuptools import setup, find_namespace_packages

setup(
    name="delta", 
    version="1.0.0", 
    packages=find_namespace_packages(),
    include_package_data=True, 
    py_modules=["delta"], 
    install_requires=[
        "rich",
        "requests",
        "tqdm",
        "pyyaml",
    ],
    entry_points={
        'console_scripts': [
            'delta=delta:main', 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12', 
    author="sh4dowByte", 
    author_email="Ahmad Juhdi <ahmadjuhdi007@gmail.com>",
)
