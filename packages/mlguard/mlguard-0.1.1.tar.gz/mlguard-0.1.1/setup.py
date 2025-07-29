from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mlguard',
    version='0.1.1',
    author='Hetrajsinh Jadeja',
    author_email='het1@gmail.com',
    description='A scikit-learn based library for model validation checks like overfitting, imbalance, bias, etc.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HDJadeja/mlguard',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'matplotlib',
        'statsmodels'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    python_requires='>=3.7',
)
