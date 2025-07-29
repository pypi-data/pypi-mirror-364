
from setuptools import setup, find_packages

setup(
    name='satya-1',
    version='0.1.2',
    packages=find_packages(),
    description='Satya - Educational Python interpreter for data structures and algorithms in natural language.',
    long_description=open('README.md').read() if __import__('os').path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Satya Bharadwaj Vemparala',
    author_email='vvempara@gitam.in.com',
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
