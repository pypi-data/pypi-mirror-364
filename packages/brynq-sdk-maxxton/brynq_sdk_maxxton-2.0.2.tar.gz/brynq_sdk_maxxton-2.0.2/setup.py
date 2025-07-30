from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_maxxton',
    version='2.0.2',
    description='Maxxton wrapper from BrynQ',
    long_description='Maxxton wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    package_data={'brynq_sdk_maxxton': ['templates/*']},
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
    ],
    zip_safe=False,
)