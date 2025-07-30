import os
from setuptools import setup, find_packages

setup(
    name='generateur-app-django',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'generateur-django = generateur_app_django.main:create_app_structure',
        ],
    },
    author='Mar',
    author_email='mar12@gmail.com',
    description='Un outil pour générer une app Django avec une arborescence personnalisée.',
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
