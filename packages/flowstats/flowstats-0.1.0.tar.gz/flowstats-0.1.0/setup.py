from setuptools import setup, find_packages

setup(
    name='mathplotlib',  # your package name
    version='0.1.0',
    description='Trace file parser and visualizer for NS2/NS3 flow stats',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ayush Chadha',
    author_email='you@example.com',
    url='https://github.com/yourusername/mathplotlib',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
