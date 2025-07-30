from setuptools import setup, find_packages

setup(
    name='django-amahapp',
    version='0.4.0',
    packages=find_packages(),
    include_package_data=True,
    description='Application Django pour tracer l’activité des utilisateurs',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Esther Kouao',
    author_email='estherkouao@gmail.com',
    url='https://github.com/tonpseudo/django-amahapp',
    license='MIT',
    install_requires=[
        'Django>=3.2.4',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
