from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mlguard',
    version='0.1.2',
    author='Hetrajsinh Jadeja',
    author_email='hetrajadeja01@gmail.com',
    description='A diagnostic toolkit for evaluating machine learning models. MLGuard provides plug-and-play checks for class imbalance, overfitting, multicollinearity, bias detection, and more — built on top of scikit-learn, pandas, and statsmodels.',
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
