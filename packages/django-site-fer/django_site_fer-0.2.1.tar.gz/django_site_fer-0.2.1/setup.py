

### `setup.py`

from setuptools import setup, find_packages

setup(
    name='django_site_fer',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    description='A reusable Django app with a dynamic responsive movie website template',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='soro F M ',
    author_email='soferelaha@gmail.com',
    url='https://github.com/tonpseudo/django_site',
    license='MIT',
    install_requires=[
        'Django>=3.2',
    ],
    entry_points={
        'console_scripts': [
            'django_site_fer=django_site_fer.cli:main',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
