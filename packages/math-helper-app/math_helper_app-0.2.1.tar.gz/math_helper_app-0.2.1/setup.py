from setuptools import setup, find_packages

setup(
    name='math-helper-app',
    version='0.2.1',
    packages=find_packages(),
    description='Package simple pour vérifier si un nombre est pair ou impair',
    author='christellelou904',
    author_email='christellelou4@gmail.com',
    entry_points={
        'console_scripts': [
            'math-helper-app = app_math.cli:main',   # commande CLI à lancer dans le terminal
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[],
)
