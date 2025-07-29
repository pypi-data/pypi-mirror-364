from setuptools import setup, find_packages

setup(
    name='django-pass-gen-safe',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['django>=4.0', 'cryptography>=41.0.0'],
    description='Générateur de mots de passe et trousseau sécurisé pour Django',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Momo',
    author_email='omomo9414@gmail.com',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)