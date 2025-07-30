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

    print(f"👉 Le ab to app bhi ban gayi 'apps.{app_name},'")
    print(f"👉 Agar app register karna hai to CUSTOM_APPS me 'apps.{app_name},' aise register karna..")