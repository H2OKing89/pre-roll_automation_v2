# setup.py

from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pre-roll_automation_v2',  # Replace with your desired project name
    version='1.0.0',  # Initial version
    author='Quentin King',  # Replace with your name
    author_email='your.email@example.com',  # Replace with your email
    description='Automate Plex pre-roll video updates based on holidays.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/H2OKing89/pre-roll_automation_v2',  # Replace with your repository URL
    packages=find_packages(),
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    install_requires=[
        'Flask==2.3.2',
        'PyYAML==6.0',
        'python-dotenv==1.0.0',
        'schedule==1.1.0',
        'pytz==2023.3',
        'plexapi==4.0.3',
    ],
    entry_points={
        'console_scripts': [
            'pre-roll=main:main',  # Allows running the app via the command `pre-roll`
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update if using a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
