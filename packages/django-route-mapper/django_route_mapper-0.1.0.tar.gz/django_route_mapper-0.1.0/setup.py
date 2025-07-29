from setuptools import setup, find_packages

setup(
    name='django-route-mapper',
    version='0.1.0',
    description='Un outil Django pour générer une documentation des routes (URLs) en .txt',
    author='Momo',
    author_email='omomo9414@email.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
