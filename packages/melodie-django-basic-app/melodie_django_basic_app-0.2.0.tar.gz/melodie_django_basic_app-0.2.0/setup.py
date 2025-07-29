from setuptools import setup, find_packages

setup(
    name='melodie-django-basic-app',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Une app Django réutilisable ultra simple',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Mélodie',
    author_email='akamelodie74@gmail.com',
    url='',  # GitLab baby ✨
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Framework :: Django :: 4.2',
    ],
    install_requires=[
        'Django>=4.2',
    ],
)
