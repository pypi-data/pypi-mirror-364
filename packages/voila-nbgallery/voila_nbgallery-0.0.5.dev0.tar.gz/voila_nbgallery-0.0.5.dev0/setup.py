import os
from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

data_files = []
for root, dirs, files in os.walk('share'):
    root_files = [os.path.join(root, i) for i in files]
    if root_files:
        data_files.append((root, root_files))

setup(
    name="voila-nbgallery",
    version="0.0.5.dev0",
    description="Voila templates for nbgallery project",
    long_description="Voila templates for nbgallery project",
    long_description_content_type="text/markdown",
    url="https://github.com/nbgallery/voila-nbgallery",
    author='https://github.com/nbgallery',
    license='MIT',
    packages=[],
    data_files=data_files,
    include_package_data=True,
    install_requires=[
        'voila>=0.2.3',
        'voila-material~=0.4.0',
    ],
    extras_require= {
        'gridstack': ['voila-gridstack~=0.1.0'],
    },
)
