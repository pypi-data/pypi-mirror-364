from setuptools import setup, find_packages

setup(
    name='my-plot-package',  # must be unique on PyPI
    version='0.1.0',
    author='John',
    author_email='burner8997@gmail.com',
    description='A simple Matplotlib plotting package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)

