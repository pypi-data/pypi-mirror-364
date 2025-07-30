from setuptools import setup, find_packages

setup(
    name='djappgen',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'django-appgen=django_appgen.cli:main',
        ],
    },
    author='Ton Nom',
    description='Générateur d\'applications Django avec structure personnalisée.',
)
