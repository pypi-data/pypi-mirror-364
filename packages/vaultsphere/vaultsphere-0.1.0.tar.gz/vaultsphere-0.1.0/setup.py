from setuptools import setup, find_packages

setup(
    name='vaultsphere',
    version='1.0.0',
    description='Encrypted NoSQL JSON database for Python',
    author='zzzNeet',
    #author_email='',
    packages=find_packages(),
    install_requires=[
        'cryptography>=41.0.0'
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
