from setuptools import setup, find_packages

setup(
    name='groupdups',
    version='0.1.0',
    author='Harsh Laghave',
    author_email='harshlaghave17@gmail.com',
    description='Group duplicate values in a list with their index positions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
   
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
