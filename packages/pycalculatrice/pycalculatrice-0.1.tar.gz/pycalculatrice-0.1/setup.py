from setuptools import setup, find_packages

setup(
    name='pycalculatrice',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,  # Important pour inclure templates, fichiers statics, etc.
    description='Une simple calculatrice Python/Django',
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
