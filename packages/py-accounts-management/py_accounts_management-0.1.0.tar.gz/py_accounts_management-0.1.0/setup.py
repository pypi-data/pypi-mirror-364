import os
from setuptools import find_packages, setup

# Utility function to read the README.md file.
# This is used for the 'long_description' on PyPI.


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Get the version from the __init__.py file of your Django app.
# This ensures the version number is kept in a single source of truth.
# You MUST update __version__ in account_levels/__init__.py for each new release.


try:
    from django_accounts_management import __version__
except ImportError:
    # Fallback for when the package is not yet installed or __init__.py is not directly accessible
    # This should ideally be caught by proper build environment setup, but provides robustness.
    __version__ = '0.0.0' # Default to 0.0.0 if version cannot be read

setup(
    # --- Essential Package Information ---
    # The name your package will be listed under on PyPI.
    # This is what users will type: `pip install django-account-levels`
    name='py-accounts-management',          
    
    # The current version of your package.
    # This should strictly follow Semantic Versioning (e.g., 0.1.0, 1.0.0).
    version=__version__,                    
    
    # A short, one-sentence summary of your package.
    description='A reusable Django app for managing flexible user account levels and access control.',
    
    # The long description, usually the content of your README.md.
    long_description=read('README.md'),
    # Specify the format of your long description (e.g., 'text/markdown').
    long_description_content_type='text/markdown', 
    
    # The URL for your project's homepage (e.g., your GitHub repository).
    url='https://github.com/asasking/py-accounts-management', # <<< IMPORTANT: Verify/Change this to your actual GitHub repo URL

    # Your name or organization name.
    author='Davidi Amoni Bilikwija', 
    # Your contact email address.
    author_email='atugonzabilikwija@gmail.com', 

    # The license under which your package is distributed.
    # This should match the content of your LICENSE file.
    license='MIT', 

    # --- Package Content Discovery ---
    # `find_packages()` automatically finds all Python packages (directories containing __init__.py)
    # within the directory containing setup.py.
    # We exclude 'tests' and 'tests.*' to prevent your test suite from being packaged.
    packages=find_packages(exclude=['tests', 'tests.*']),
    
    # This tells setuptools to include non-Python files (like templates, static files, migrations)
    # that are specified in your MANIFEST.in file. This is crucial for Django apps.
    include_package_data=True,

    # --- Dependencies ---
    # List of Python packages required by your package.
    # Specify minimum versions to ensure compatibility.
    install_requires=[
        'Django>=5.0', # Specify the minimum Django version your app supports
        # Add any other third-party Python libraries your app directly depends on here.
        # Example: 'requests>=2.20.0', 'Pillow>=8.0.0'
    ],
    
    # Specify which Python versions your package supports.
    # This is important for PyPI to filter compatibility.
    # Example: Supports Python 3.9 up to (but not including) Python 4.0.
    python_requires='>=3.9', 

    # --- Classifiers (for PyPI search and categorization) ---
    # A list of standard classifiers that describe your project.
    # Find more at https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 5 - Production/Stable', 
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2', # Specific Django versions you test against
        'Framework :: Django :: 5.0', # Add other versions you support
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # Match your chosen license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    # --- Keywords (optional, for PyPI search) ---
    # A space-separated string of keywords.
    keywords='django account levels user management roles permissions access control',

   
)