from setuptools import setup, find_packages
from pathlib import Path

# Lire le contenu du README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='create-app-savane',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description="Générateur de structure d'app Django personnalisée",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SAVANE Mouhamed',
    author_email='savanemouhamed05@gmail.com',
    entry_points={
        'console_scripts': [
            'create-app = create_app.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
    ],
    python_requires='>=3.6',
    install_requires=[],
)
