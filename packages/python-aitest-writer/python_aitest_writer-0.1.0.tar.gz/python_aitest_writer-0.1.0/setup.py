from setuptools import setup, find_packages

setup(
    name='python_aitest_writer',
    version='0.1.0',
    description='Generate pytest test cases for your Python app using Claude AI',
    long_description=open('README-pypi.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/python_aitest_writer',
    packages=find_packages(),
    install_requires=[
        'pytest',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'python-aitest-writer=python_aitest_writer.generate_test_cases:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
) 