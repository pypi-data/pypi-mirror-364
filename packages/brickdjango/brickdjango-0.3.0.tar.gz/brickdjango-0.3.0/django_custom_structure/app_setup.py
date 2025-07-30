import os
import subprocess
import sys

from .app_config import fix_appconfig_name

def create_app(app_name):
    base_path = os.getcwd()
    manage_path = os.path.join(base_path, 'manage.py')

    # ✅ Ensure this is a Django project directory
    if not os.path.exists(manage_path):
        print("❌ Error: manage.py nhi mil rahi hai. Ya to tu django project ke bahar hai ya fir project nhi banaya direct app bana raha hai?")
        print("✅  Solution: 1. Check kar ki virtual env active hai...")
        print("✅  Solution: 2. Check kar ki proper project directory me hai...")
        sys.exit(1)

    # ✅ App will be created inside the "apps/" folder
    apps_dir = os.path.join(base_path, 'apps')
    os.makedirs(apps_dir, exist_ok=True)

    # ✅ Full path where the app should be created
    app_path = os.path.join(apps_dir, app_name)

    if os.path.exists(app_path):
        print(f"⚠️ Kya yar '{app_name}' ya Dir '{app_name}' pehle se hi hai tu fir se create kar raha hai.")
        print(f"👉 Kuch alag nam try kar")
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
