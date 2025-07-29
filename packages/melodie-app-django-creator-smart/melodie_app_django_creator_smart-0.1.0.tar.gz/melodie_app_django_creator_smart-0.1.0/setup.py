from setuptools import setup, find_packages

setup(
    name='melodie-app-django-creator-smart',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'melodie-app-django-creator-smart = app_creator.core:main',
        ],
    },
    author='Mélodie',
    description='Automagically generate Django apps',
    license='MIT',
    python_requires='>=3.6',
)
