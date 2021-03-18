import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ruvdsdriver',
    version='0.0.1',
    author='Sergey Mezentsev',
    author_email='thebits@yandex.ru',
    description='Libcloud driver for RU VDS',
    install_requires=['apache-libcloud>=3.0.0'],
    license='UNLICENSE',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/thebits/libcloud-ruvds',
    packages=setuptools.find_packages(),
    classifiers=[
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

