from setuptools import setup, find_packages

setup(
    name='django_visit_counter',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    description='Application Django pour personnaliser le contenu selon le nombre de visites par session.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Momo',
    author_email='omomo9414@email.com',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
