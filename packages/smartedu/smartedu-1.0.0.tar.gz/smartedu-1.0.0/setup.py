from setuptools import setup, find_packages

setup(
    name='smartedu',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[],
    author='Vinay Kumar Dubba',
    description='A CLI backend system for managing students, courses, enrollments, and grades.',
    #long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://github.com/yourusername/smartedu',  # If you have one
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True
)
