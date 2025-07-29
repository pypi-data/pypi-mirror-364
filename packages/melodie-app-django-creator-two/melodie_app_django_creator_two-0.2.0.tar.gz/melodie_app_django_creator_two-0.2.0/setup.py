from setuptools import setup, find_packages

setup(
    name='melodie-app-django-creator-two',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'melodie-app-django-creator-two = app_creator.core:main',
        ],
    },
    author='Mélodie',
    description='Automagically generate Django apps',
    license='MIT',
    python_requires='>=3.6',
)
