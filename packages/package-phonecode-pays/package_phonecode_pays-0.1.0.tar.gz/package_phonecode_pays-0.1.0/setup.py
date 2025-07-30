from setuptools import setup, find_packages

setup(
    name='package_phonecode_pays',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    description='Package Django pour obtenir l’indicatif téléphonique selon le pays',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='ParfaiteSekongo',
    author_email='p88971582@gmail.com',
    license='MIT',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['django>=3.2'],
)
