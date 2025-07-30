# setup.py
from setuptools import setup, find_packages

setup(
    name='django-login-activity',
    version='0.0.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=3.2'
    ],
    description='Package Django pour enregistrer les connexions et déconnexions des utilisateurs.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Ton Nom',
    author_email='ton.email@example.com',
    url='https://github.com/tonprofil/django-login-activity',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'login-activity = login_activity.cli:main',
        ],
    },
)
