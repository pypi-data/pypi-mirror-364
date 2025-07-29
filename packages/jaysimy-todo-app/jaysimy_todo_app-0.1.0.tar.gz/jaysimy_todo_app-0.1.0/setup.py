from setuptools import setup, find_packages

setup(
    name='jaysimy-todo_app',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Une application Django simple de gestion de tâches (To-Do List).',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='jay-simy',
    author_email='simyjeanpaul@gmail.com',
    classifiers=[
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=[
        'Django>=3.2',
    ],
)
