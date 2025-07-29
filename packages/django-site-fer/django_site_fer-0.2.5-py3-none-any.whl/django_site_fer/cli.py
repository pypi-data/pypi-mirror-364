import sys
from django_site_fer.generate import generate_project

def main():
    if len(sys.argv) < 3 or sys.argv[1] != 'generate':
        print("Usage: django_site_fer generate <project_name>")
        sys.exit(1)
    project_name = sys.argv[2]
    generate_project(project_name)

if __name__ == "__main__":
    main()
