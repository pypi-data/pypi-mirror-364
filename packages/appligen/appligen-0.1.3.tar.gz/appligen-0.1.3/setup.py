from setuptools import setup, find_packages

setup(
    name='appligen',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Un classificateur d''age',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='jay-simy',
    author_email='simyjeanpaul@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'django>=4.0',
    ],
)