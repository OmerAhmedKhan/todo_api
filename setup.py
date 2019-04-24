""" Sets up Hem API """
from setuptools import setup, find_packages

VERSION = '0.1.01'

setup(
    name='hem_test_api',
    version=VERSION,
    description='Hem test Api',
    long_description='Hem Test providing web services to Basic TODO List',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3'
    ],
    keywords='oak hem test api',
    author='Omer Ahmed Khan',
    author_email='omerahmed122@gmail.com',
    url='',
    license='',
    packages=find_packages(),
    install_requires=['flask-restful', 'requests'],
    include_package_data=True,
    zip_safe=False
)