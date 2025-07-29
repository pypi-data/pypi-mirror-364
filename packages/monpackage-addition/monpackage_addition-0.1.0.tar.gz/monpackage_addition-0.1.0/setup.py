from setuptools import setup, find_packages

setup(
    name='monpackage-addition',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'addition-cli=monpackage.cli:main',
        ],
    },
    description='Package avec addition et CLI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='ParfaiteSekongo',
    author_email='p88971582@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
