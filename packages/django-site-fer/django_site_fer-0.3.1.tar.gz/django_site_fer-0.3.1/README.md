# django_site

A reusable Django app to generate a dynamic and responsive movie website template.

## Installation

```bash
pip install django_site_fer

django_site_fer generate myproject
cd myproject
python manage.py runserver

##conseil## 
# si le server ne se lance pas , tu dois corriger le champ name dans le fichier apps.py de ton application ,tu veras forcement comme suit ,name = 'django_site' change le en ,name = 'django_site_fer' 