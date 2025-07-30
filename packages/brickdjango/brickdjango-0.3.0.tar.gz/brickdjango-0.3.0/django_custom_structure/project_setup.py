import os
import subprocess
import sys

from django_custom_structure.docker_data import DOCKER_CONTENT
from django_custom_structure.git_data import GIT_IGNORE_CONTENT
from django_custom_structure.setting_data import DEVELOPMENT_SETTING_BLOCK, PRODUCTION_SETTING_BLOCK
from django_custom_structure.base_data import BASE_SETTING


def create_project(project_name):
    base_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(base_path):
        print(f"❌ Error: Abe yar '{project_name}' ye project pehle se hi hai yaha {base_path}")
        print(f"👉 Kuch alag nam try kar accha sa..")
        sys.exit(1)

    os.makedirs(base_path, exist_ok=True)

    # Create virtual environment
    venv_path = os.path.join(base_path, 'venv')
    subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)

    # Determine OS-specific paths and executable names
    if sys.platform == 'win32':
        venv_bin_dir = 'Scripts'
        pip_executable = 'pip.exe'
        django_admin_executable = 'django-admin.exe'
    else:
        venv_bin_dir = 'bin'
        pip_executable = 'pip'
        django_admin_executable = 'django-admin'

    pip_path = os.path.join(venv_path, venv_bin_dir, pip_executable)
    django_admin_path = os.path.join(venv_path, venv_bin_dir, django_admin_executable)

    # Install Django
    subprocess.run([pip_path, 'install', 'django'], check=True)

    # Install django-environ
    subprocess.run([pip_path, 'install', 'django-environ'], check=True)

    # Start Django project
    subprocess.run([
        django_admin_path,
        'startproject', 'config', base_path
    ], check=True)

    # Create folder structure
    os.makedirs(os.path.join(base_path, 'config', 'settings'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'apps'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'base'), exist_ok=True)

    # Move settings.py to settings/base.py and replace contents with BASE_SETTING
    old_settings = os.path.join(base_path, 'config', 'settings.py')
    new_base_settings = os.path.join(base_path, 'config', 'settings', 'base.py')

    with open(new_base_settings, 'w') as f:
        f.write(BASE_SETTING)

    # Create dev and prod settings files
    dev_settings = os.path.join(base_path, 'config', 'settings', 'development.py')
    prod_settings = os.path.join(base_path, 'config', 'settings', 'production.py')

    # Init settings package and apps package
    open(os.path.join(base_path, 'config', 'settings', '__init__.py'), 'a').close()
    open(os.path.join(base_path, 'apps', '__init__.py'), 'a').close()
    open(os.path.join(base_path, 'base', '__init__.py'), 'a').close()

    env_path = os.path.join(base_path, 'config', 'settings', '.env')
    open(env_path, 'a').close()

    sec_key = None
    if os.path.exists(old_settings):
        with open(old_settings, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if 'SECRET_KEY' in line:
                sec_key = line.strip()
                break

        if sec_key:
            sec_key_clean = "".join(sec_key.split())
            with open(env_path, 'a') as f:
                f.write(f'{sec_key_clean}\n')
        else:
            pass

    with open(prod_settings, 'w') as f:
        f.write('\n' + PRODUCTION_SETTING_BLOCK + '\n')

    with open(dev_settings, 'w') as f:
        f.write('\n' + DEVELOPMENT_SETTING_BLOCK + '\n')


    manage_py_path = os.path.join(base_path, 'manage.py')

    if os.path.exists(manage_py_path):
        with open(manage_py_path, 'r') as f:
            content = f.read()

        new_content = content.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')",
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')"
        )

        if os.path.exists(old_settings):
            os.remove(old_settings)

        with open(manage_py_path, 'w') as f:
            f.write(new_content)


    # Write .gitignore
    with open(os.path.join(base_path, '.gitignore'), 'w') as f:
        f.write(GIT_IGNORE_CONTENT.strip())

    # Write Dockerfile
    dockerfile_path = os.path.join(base_path, "Dockerfile")
    with open(dockerfile_path, 'w') as f:
        f.write(DOCKER_CONTENT.strip())

    # Create requirements.txt using pip freeze from the venv
    with open(os.path.join(base_path, 'requirements.txt'), 'w') as req_file:
        subprocess.run([pip_path, 'freeze'], stdout=req_file, check=True)

    # ✅ Final success message
    print(f"\n🎉 YeLe bhai ban gaya tera project, '{project_name}' ye project ka nam aur {base_path} ye project location.")
    print("👉 Ab age kya karna hai dhyan se padh le...")
    print(f"   1. Project directory me ja, cd {project_name}")
    print("   2. Ab virtual environment ko active kar.")
    print("   3. Activate hone ke bad server run kar.")
    print("   🎬😅   python manage.py runserver")
    print("   ⚠️ Important Note 🧱⚙️")
    print("""
    Agar aapko naya app create karna hai? 🧐
    🐍 Pehle, venv activate karo

    Phir command run karo:
        djangobrick startapp <app_name>

    🧱 Isse kya hoga?
    ➡️ Naya app create hoga is path par: apps/<app_name>

    📦 Ye app, apps folder ke andar neatly place hoga — structure clean rahega!

    🔹 App ko project me register karna hai?
    Toh CUSTOM_APPS list me add karo with prefix:
        'apps.<app_name>'

    🧠 Prefix yaad rakhna — 'apps.' likhna mandatory hai,
    warna Django confuse ho jayega 😵‍💫
    """)

    print("Le ab moj kar 🎉 🐙")

