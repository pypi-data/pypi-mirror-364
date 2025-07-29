from setuptools import setup, find_packages

setup(
    name='liste_etudiants',  # Nom unique sur PyPI
    version='0.1.0',
    description='Package pour générer des noms d\'étudiants aléatoires',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Monique',
    author_email='ton.email@example.com',
    url='https://github.com/tongithub/liste_etudiants',  # optionnel
    packages=find_packages(),
    install_requires=[
        'Faker',
    ],
    entry_points={
        'console_scripts': [
            'gen-etudiants=liste_etudiants.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
