from setuptools import setup, find_packages

setup(
    name='django-anemie',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Une application Django pour sensibiliser à l’anémie sévère chez les jeunes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ton-utilisateur/django-anemie',
    author='Ton Nom',
    author_email='ton.email@example.com',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['Django>=3.2'],
)
