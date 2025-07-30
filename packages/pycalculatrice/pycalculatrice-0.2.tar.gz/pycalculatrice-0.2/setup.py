from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pycalculatrice',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,  # Important pour inclure templates, fichiers statics, etc.
    description='Une simple calculatrice Python/Django',
    long_description=long_description,               # Ajout de la description longue
    long_description_content_type='text/markdown',   # Précise que c’est du markdown
    author='Monique Reine',
    author_email='ton.email@example.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'django>=3.0',  # préciser la dépendance Django
    ],
)
