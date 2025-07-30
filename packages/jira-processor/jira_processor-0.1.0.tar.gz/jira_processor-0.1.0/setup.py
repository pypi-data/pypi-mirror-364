from setuptools import setup, find_packages

setup(
    name='jira_processor',  # Your package name
    version='0.1.0',  # Package version
    description='A library to process JIRA issues and generate summaries.',
    author='hannah biju',
    author_email='hb7379@zebra.com',
    packages=find_packages(),  # Automatically find package directories
    install_requires=[
        'jira',
        'python-dotenv',
        'openai',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
