from setuptools import setup, find_packages

setup(
    name='quiz_jeu',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2',
    ],
    description='Jeu de quiz simple et facile.',
    author='Lou Chrsitelle',
    author_email='christellelou4@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)