from setuptools import setup, find_packages

setup(
    name='quiz_jeu',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2',
    ],
    description='Un nettoyeur de texte simple pour Django.',
    author='Votre Nom',
    author_email='votre.email@example.com',
    url='https://github.com/votrecompte/quiz_jeu',  # Remplacez par l'URL de votre dépôt
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)