from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='modelstack',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['click', 'tabulate', 'joblib', 'torch', 'scikit-learn', 'numpy'],
    entry_points={
        'console_scripts': [
            'modelstack = modelstack.cli:cli',
        ],
    },
    author='Aniruddha',
    author_email='aniruddhakide16@example.com',
    description='ModelStack - Lightweight Local Model Registry',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Aniruddh-k/modelstack',  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)