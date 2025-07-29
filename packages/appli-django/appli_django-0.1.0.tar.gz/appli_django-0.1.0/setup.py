from setuptools import setup, find_packages

setup(
    name='appli-django',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'appli-django=appli_django.cli:main',
        ],
    },
    author='Nicosidick',
    description='Un outil CLI pour créer des applications Django automatiquement.',
    license='MIT',
    python_requires='>=3.6',
)
