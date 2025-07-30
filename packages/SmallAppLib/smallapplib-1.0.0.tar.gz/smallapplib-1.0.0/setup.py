from setuptools import (
    setup,
    find_packages
)


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='SmallAppLib',
    version='1.0.0',
    author='Cupcake_wrld',
    author_email='evilprog@yandex.ru',
    description='App for simple console app building',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent'
    ],
    keywords='files small console ',
    # project_urls={
    #     'GitHub': 'Bob-Jacka'
    # },
    python_requires='>=3.12'
)
