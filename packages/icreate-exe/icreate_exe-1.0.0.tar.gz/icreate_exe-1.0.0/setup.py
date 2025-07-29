from setuptools import setup, find_packages

setup(
    name='icreate-exe',
    version='1.0.0',
    description='Приложение для создания exe файла из .py',
    long_description=open('./README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    author='Ilia Miheev',
    author_email='strict-swept-unify@duck.com',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'pyinstaller'
    ],
    entry_points={
        'console_scripts': [
            'icreate-exe=icreateExe.icreateExe:icreateExe',
        ],
    },
)
