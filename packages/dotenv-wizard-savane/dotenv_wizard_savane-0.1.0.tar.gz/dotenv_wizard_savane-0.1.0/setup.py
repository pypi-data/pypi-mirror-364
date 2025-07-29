from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name='dotenv-wizard-savane',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Assistant CLI pour créer et gérer les fichiers .env dans vos projets Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SAVANE Mouhamed',
    author_email='savanemouhamed05@gmail.com',
    entry_points={
        'console_scripts': [
            'dotenv-wizard = dotenv_wizard.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)
