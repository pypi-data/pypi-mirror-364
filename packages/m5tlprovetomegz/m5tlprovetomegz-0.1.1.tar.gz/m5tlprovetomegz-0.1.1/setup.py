from setuptools import setup, find_packages

setup(
    name='m5tlprovetomegz',
    version='0.1.1',
    packages=find_packages(),
    author='m5tl',
    description='وصف قصير للمكتبة',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
