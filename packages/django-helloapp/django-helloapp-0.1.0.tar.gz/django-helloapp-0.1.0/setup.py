from setuptools import setup, find_packages

setup(
    name='django-helloapp',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Une app Django de démo',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ton Nom',
    author_email='ton@email.com',
    install_requires=['Django>=3.2'],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
