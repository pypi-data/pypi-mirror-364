from setuptools import setup, find_packages

setup(
    name='package_genere',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    description='Générateur d’app Django avec urls.py intégré',
    author='NDA',
    author_email='angecedricnda6@gmail.com',
    entry_points={
        'console_scripts': [
            'django-appgen=django_appgen.cli:create_app',
        ],
    },
    python_requires='>=3.6',
)
