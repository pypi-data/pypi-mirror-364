from setuptools import setup, find_packages

setup(
    name='django-custom-appgen',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'djappgen=app_generator.generate_django_app:main',
        ],
    },
    install_requires=[],
    author='kelly',
    license='MIT',
    description="Générateur d'app Django avec structure personnalisée",
    long_description="Génère une app Django avec des dossiers models/, views/, templates/, static/, etc.",
    long_description_content_type='text/markdown',
    url='https://github.com/kellykomenan/django-custom-appgen',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


