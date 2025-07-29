from setuptools import setup, find_packages
setup(
    name='start_app_mai',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Générateur de structure d\'app Django personnalisée',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='soro F M',
    author_email='soferelaha@gmail.com',
    entry_points={
        'console_scripts': [
            'start_app_mai= start_app_mai.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[],
)