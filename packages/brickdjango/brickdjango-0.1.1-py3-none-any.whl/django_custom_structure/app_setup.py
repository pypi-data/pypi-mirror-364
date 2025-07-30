import os
import subprocess
import sys

from .app_config import fix_appconfig_name

def create_app(app_name):
    base_path = os.getcwd()
    manage_path = os.path.join(base_path, 'manage.py')

    # ✅ Ensure this is a Django project directory
    if not os.path.exists(manage_path):
        print("❌ Error: manage.py not found. Are you in the root of a Django project?")
        sys.exit(1)

    # ✅ App will be created inside the "apps/" folder
    apps_dir = os.path.join(base_path, 'apps')
    os.makedirs(apps_dir, exist_ok=True)

    # ✅ Full path where the app should be created
    app_path = os.path.join(apps_dir, app_name)

    if os.path.exists(app_path):
        print(f"⚠️ App '{app_name}' or Dir '{app_name}' already exists.")
        sys.exit(1)

    app_final_path = os.path.join(apps_dir, app_name)
    os.makedirs(app_final_path, exist_ok=True)
    # print(app_final_path)

    # ✅ Call "python manage.py startapp" to use project settings
    subprocess.run([
        sys.executable,
        'manage.py',
        'startapp',
        app_name,
        app_path
    ], check=True)

    print(f"✅ App '{app_name}' created at {app_path}")

    fix_appconfig_name(apps_dir, app_name)
