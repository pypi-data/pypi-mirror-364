from setuptools import setup, find_packages

setup(
    name='package_aram',
    version='0.1.6',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Un petit package Django qui cree des app ',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='ynaffit_aes',
    author_email='aramsamb02@gmail.com',
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

    entry_points={
        'console_scripts':[
            'generate-django-app = package_aram.cli:main',
        ]
    }

)