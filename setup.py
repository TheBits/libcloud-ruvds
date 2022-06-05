import setuptools

long_description = "[Libcloud](https://libcloud.apache.org/) driver for [https://ruvds.com/](https://ruvds.com/)"

setuptools.setup(
    name="ruvdsdriver",
    version="0.0.1",
    author="Sergey Mezentsev",
    author_email="thebits@yandex.ru",
    description="Libcloud driver for RU VDS",
    install_requires=["apache-libcloud>=3.0.0"],
    license="UNLICENSE",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/thebits/libcloud-ruvds",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
