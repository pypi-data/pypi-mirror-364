from setuptools import setup, find_packages

setup(
    name='pack_app',
    version='0.2.3',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description="Générateur de structure d'application Django",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='christellelou904',
    author_email='christellelou4@gmail.com',
    entry_points={
        'console_scripts': [
            'pack_app=pack_app.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=4.0',
    ],
    python_requires='>=3.6',
)
