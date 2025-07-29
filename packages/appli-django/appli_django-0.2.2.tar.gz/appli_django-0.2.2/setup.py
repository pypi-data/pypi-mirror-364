from setuptools import setup, find_packages

setup(
    name='appli-django',
    version='0.2.2',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'appli-django=appli_django.cli:main',
        ],
    },
    author='Nicosidick',
    description='Un outil CLI pour créer des apps Django automatiquement.',

    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',  # ⬅️ TRÈS IMPORTANT

    license='MIT',
    python_requires='>=3.6',
)
