from setuptools import setup, find_packages

setup(
    name='decisioncanvas',
    version='0.1.0',
    description='Easy decision boundary visualization for classifiers',
    author='Your Name',
    author_email='youremail@example.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scikit-learn',
        'matplotlib',
    ],
    python_requires='>=3.7',
    url='https://github.com/yourusername/decisioncanvas',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
