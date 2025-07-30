from setuptools import setup, find_packages

setup(
    name='modelstack',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['click', 'tabulate', 'joblib', 'torch','scikit-learn','numpy'],
    entry_points={
        'console_scripts': [
            'modelstack = modelstack.cli:cli',
        ],
    },
    author='Aniruddha',
    description='ModelStack - Lightweight Local Model Registry',
    python_requires='>=3.7',
)