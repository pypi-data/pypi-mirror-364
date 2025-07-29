from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='akihiro',
    version='1.6.0',
    packages=find_packages(),
    install_requires=['requests', 'faker', 'sumy', 'googletrans'],
    author='Darrien Rafael Wijaya',
    author_email='darrienwijaya@gmail.com',
    description='Python package to enhance programming experience with AI LLM capabilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Akihiro2004/akihiro',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
    include_package_data=True,
)