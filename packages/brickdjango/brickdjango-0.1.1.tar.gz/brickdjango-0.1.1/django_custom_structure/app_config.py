import os

def fix_appconfig_name(apps_dir, app_name):
    app_path = os.path.join(apps_dir, app_name)
    apps_py_path = os.path.join(app_path, 'apps.py')

    if not os.path.exists(apps_py_path):
        print(f"❌ {apps_py_path} not found!")
        return

    with open(apps_py_path, 'r') as f:
        lines = f.readlines()

    # Modify the line that sets "name = ..."
    with open(apps_py_path, 'w') as f:
        for line in lines:
            if line.strip().startswith('name ='):
                f.write(f"    name = 'apps.{app_name}'\n")
            else:
                f.write(line)

    print(f"👉 To register your app in CUSTOM_APPS use app as prefix like'apps.{app_name},'")