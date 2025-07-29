from setuptools import setup, find_packages
setup(
    name='djkelly_app',
    version='0.3.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Générateur de structure d\'app Django personnalisée',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='kelly',
    author_email='kellylajuana@gmail.com',
    entry_points={
        'console_scripts': [
            'djkelly_app = djangopackage.djkelly_app.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[],
)