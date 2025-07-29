import os
import shutil

def generate_project(project_name):
    os.makedirs(project_name, exist_ok=True)
    # Crée un nouveau projet Django avec django-admin
    os.system(f'django-admin startproject {project_name} {project_name}')
    
    # Copie l'app site dans le projet
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_app_dir = os.path.join(current_dir, '..', 'django_site_fer')
    target_app_dir = os.path.join(project_name, 'django_site_fer')
    
    if os.path.exists(target_app_dir):
        shutil.rmtree(target_app_dir)
    shutil.copytree(source_app_dir, target_app_dir)
    
    # Modifier settings.py pour ajouter 'sitefere' dans INSTALLED_APPS et configurer STATICFILES_DIRS
    settings_path = os.path.join(project_name, project_name, 'settings.py')
    with open(settings_path, 'r') as f:
        content = f.read()
    if "'django_site_fer'" not in content:
        content = content.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'django_site_fer',"
        )
    if "import os" not in content:
        content = "import os\n" + content
    if "STATICFILES_DIRS" not in content:
        content += "\nSTATICFILES_DIRS = [os.path.join(BASE_DIR, 'django_site_fer', 'static')]\n"
    with open(settings_path, 'w') as f:
        f.write(content)
    
    # Modifier urls.py pour inclure sitefere.urls
    urls_path = os.path.join(project_name, project_name, 'urls.py')
    with open(urls_path, 'r') as f:
        urls_content = f.read()
    if "include('django_site_fer.urls')" not in urls_content:
        urls_content = urls_content.replace(
            "from django.urls import path",
            "from django.urls import path, include"
        )
        urls_content = urls_content.replace(
            "urlpatterns = [",
            "urlpatterns = [\n    path('', include('django_site_fer.urls')),"
        )
        with open(urls_path, 'w') as f:
            f.write(urls_content)
    
    print(f"Project '{project_name}' generated successfully.")
