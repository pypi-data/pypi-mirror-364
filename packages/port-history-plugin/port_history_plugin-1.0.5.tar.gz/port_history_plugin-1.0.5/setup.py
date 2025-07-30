from setuptools import find_packages, setup

setup(
    name='port-history-plugin',
    version='1.0.5',
    url='',
    description='Check the relevance of inventory on switches',
    author='Nikolay Gimozdinov',
    author_email='',
    install_requires=["aiosnmp","netutils"],
    packages=find_packages(),
    license='MIT',
    include_package_data=True,
    keywords=['netbox', 'netbox-plugin', 'plugin'],
)
