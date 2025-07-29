from setuptools import setup, find_packages

setup(
    name='appli-django',
    version='0.2.9',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'appli-django=appli_django.cli:main',
        ],
    },
    author='Nicosidick',
    description='Créer rapidement une structure complète d\'application Django.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    python_requires='>=3.6',
)
