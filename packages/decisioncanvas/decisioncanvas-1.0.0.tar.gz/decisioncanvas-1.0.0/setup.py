from setuptools import setup, find_packages

setup(
    name='decisioncanvas',
    version='1.0.0',
    description='Easy decision boundary visualization for classifiers',
    author='Krunal Wankhade, Parimal Kalpande',
    author_email='krunal.wankahde1810@gmail.com',
    url='https://github.com/KrunalWankhade9021/Decesion-Canvas',
    packages=find_packages(exclude=['tests*', 'examples*']),  # cleaner packaging
    install_requires=[
        'numpy>=1.18.0',
        'scikit-learn>=0.24.0',
        'matplotlib>=3.2.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='visualization, classifier, decision boundary, matplotlib, scikit-learn',
    license='MIT',
    include_package_data=True,
)
