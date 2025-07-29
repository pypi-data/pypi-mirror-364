# melodie-django-basic-app

Une app Django toute simple, réutilisable .

## Installation


## Utilisation

Ajoute `'melodie-django-basic-app'` dans `INSTALLED_APPS`.

Inclure ses URLs dans ton projet principal :

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path('demo/', include('melodie-django-basic-app.urls')),
]

---
###  `setup.py`
```python
from setuptools import setup, find_packages

setup(
    name='melodie-django-basic-app',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Une app Django réutilisable ultra simple',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Mélodie',
    author_email='akamelodie74@gmail.com',
    url='https://gitlab.com/melodie/melodie-django-basic-app', 
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Framework :: Django :: 4.2',  # adapter selon ta cible
    ],
    install_requires=[
        'Django>=4.2',
    ],
)

