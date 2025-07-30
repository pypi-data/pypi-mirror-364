from setuptools import setup, find_packages
import os

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('shit/web/static')

setup(
    name='Shitventure',
    version='1.0.0.1',
    packages=find_packages(),
    package_data={'': extra_files},
    description='这个夏天，让我们一起为了拉屎再次失眠',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Shitventure',
    author_email='support@shitventure.com',
    license='MIT',
    python_requires='>=3.6',
    install_requires=[
        'Flask>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'shit=shit:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
