from setuptools import setup, find_packages

setup(
    name='password-generator-kamax',
    version='0.4.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Un générateur de mots de passe sécurisé en ligne de commande et en Python',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='kamax',
    author_email='blab97400@gmail.com',
    entry_points={
        'console_scripts': [
            'generate-password = password_generator.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

