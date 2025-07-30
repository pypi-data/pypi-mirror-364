from setuptools import setup, find_packages

setup(
    name='ryo',
    version='0.1.8',
    packages=find_packages(),
    install_requires=['PyYAML', 'yamale', 'boto3', 'tenacity'],
    entry_points={
        'console_scripts': [
            'ryo=ryo.cli:main', 
        ],
    },
    author='Ana Victoria de Oliveira Silva',
    author_email='anavictoriaavos@gmail.com',
    description='A personal CLI tool using YAML and schema validation.',
    license='MIT',
    python_requires='>=3.7',
)
