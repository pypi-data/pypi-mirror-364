from setuptools import setup, find_packages

setup(
    name='appligen',
    version='0.2.7',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Un package qui genere une application django.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='jay-simy',
    author_email='simyjeanpaul@gmail.com',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Build Tools',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'envgen=envgen.cli:main',  # ← adapte ce chemin si ton module diffère
        ],
    },
    install_requires=[
        'python-dotenv>=1.0.0',
    ],
)


