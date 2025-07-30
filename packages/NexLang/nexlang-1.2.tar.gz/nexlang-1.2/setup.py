from setuptools import setup, find_packages

setup(
    name='NexLang',
    version='1.2',
    packages=find_packages(),
    author='D',
    author_email='nasr2python@gmail.com',
    description='What',
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