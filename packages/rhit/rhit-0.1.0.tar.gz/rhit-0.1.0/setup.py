from setuptools import setup, find_packages

setup(
    name='rhit',
    version='0.1.0',
    author='Rohit',
    author_email='rohitmbl24@gmail.com.com',
    description='A brief description of the rhit package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/imrohit/rhit',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)