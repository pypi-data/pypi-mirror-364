from setuptools import setup, find_packages
setup(
    name='custom-app-momo',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Générateur de structure d\'app Django personnalisée',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Mohamed',
    author_email='omomo9414@gmail.com',
    entry_points={
        'console_scripts': [
            'custom-app = custom_app.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[],
)