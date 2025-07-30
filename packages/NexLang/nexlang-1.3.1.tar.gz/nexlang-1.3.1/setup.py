from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='NexLang',
    version='1.3.1',
    packages=find_packages(),
    author='D',
    author_email='nasr2python@gmail.com',
    description='Super obfuscation Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    package_data={
        '': ['*.so'],
    },
    zip_safe=False
)