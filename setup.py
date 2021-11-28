from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='unitoad',
    version='0.0.1',
    description="Encode binary data into valid UTF-8 characters.",
    long_description=readme(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.10',
        'Topic :: System :: Archiving :: Compression',
    ],
    keywords='unicode str bytes',
    url='https://github.com/AJMansfield/unitoad',
    author='Anson Mansfield',
    author_email='anson.mansfield@gmail.com',
    license='Apache License 2.0',
    packages=['unitoad'],
    install_requires=[
    ],
    tests_require=[
        'pytest',
    ],
    include_package_data=True,
    zip_safe=True,
)