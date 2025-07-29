from setuptools import setup, find_packages

setup(
    name='django-calcul',
    version='0.3.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Nicosidick',
    author_email='abou210traore@gmail.com',
    entry_points={
        'console_scripts': [
            'django-calcul = p1.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[],
)