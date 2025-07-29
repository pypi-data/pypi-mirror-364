import os
import argparse

def create_app(app_name, directory=None):
    base_path = directory if directory else os.getcwd()
    app_path = os.path.join(base_path, app_name)
    os.makedirs(app_path, exist_ok=True)
    files = ['__init__.py', 'admin.py', 'models.py', 'views.py', 'urls.py', 'apps.py']
    for file in files:
        with open(os.path.join(app_path, file), 'w') as f:
            f.write(f'# {file} for {app_name}\n')
    print(f"App '{app_name}' created at: {app_path}")

def main():
    parser = argparse.ArgumentParser(description='Django App Creator CLI')
    parser.add_argument('command', choices=['create'], help='Command to run')
    parser.add_argument('app_name', help='Name of the Django app to create')
    parser.add_argument('--directory', '-d', help='Directory to create the app in')
    args = parser.parse_args()

    if args.command == 'create':
        create_app(args.app_name, args.directory)

if __name__ == '__main__':
    main()
