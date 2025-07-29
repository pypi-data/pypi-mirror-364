from setuptools import setup, find_packages

setup(
    name='package-nico',
    version='0.1.0',
    description='Outil pour générer automatiquement une application Django complète',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Nicosidick',
    author_email='ton.email@example.com',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=['Django>=4.0'],
    entry_points={
        'console_scripts': [
            'package-nico-app=django_nico.main:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
