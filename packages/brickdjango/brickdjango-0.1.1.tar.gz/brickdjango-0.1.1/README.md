
🔤 "BrickDjango" – Meaning in Depth
BrickDjango is a metaphorical name that combines:

"Brick" – the basic building block of construction.

"Django" – the popular Python web framework you're customizing.

🧱 What “Brick” Suggests:
Modularity: Bricks are independent units that come together to form larger structures. Similarly, your Django structure has modular apps, separated settings, and organized layout.

Foundation & Scalability: Bricks form the foundation of a strong, scalable structure. Your custom project structure aims to do the same for Django projects.

Simplicity with Power: Bricks are simple, but powerful when arranged well — just like your approach to Django project architecture.



## 📘 BrickDjango User Guide



Table of Contents


1. Installation

2. Features

3. Getting Started

4. Creating a New Project

5. Creating New Apps

6. Project Structure Overview

7. Configuring Settings

8. Best Practices

9. Troubleshooting



## 🔰 **Introduction**

**BrickDjango** is a custom Django project scaffolding tool that helps developers start Django projects and apps with a modular, scalable, and maintainable folder structure.

This guide walks you through installing, using, and extending BrickDjango.

---

## 📦 Installation

### Requirements:
- Python 3.10+
- `pip` (Python package manager)
- Virtual environment setup

### Steps:

1. Clone or install BrickDjango:

**bash**
pip install brickdjango


2. Create and activate a virtual environment:

**bash**
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


---

## ⚙️ Features

- Modular project layout (`apps/`, `config/`, `base/`)
- CLI for structured app/project creation
- Automatic app namespacing (`apps.myapp`)
- Environment-based settings (dev/prod)
- Follows Django best practices with added organization

---

## 🚀 Getting Started

Use the `brickdjango` CLI to bootstrap your projects and apps easily.

---

## 🏗️ Creating a New Project

**bash**
brickdjango startproject 


✅ This command sets up a new Django project with the custom BrickDjango folder layout.

**Example:**

**bash**
brickdjango startproject mysite
cd mysite


---

## 🧱 Creating a New App

**bash**
brickdjango startapp 

    
✅ This creates a Django app inside the `apps/` directory with proper namespace.

**Example:**

bash
brickdjango startapp blog


🔁 This will create: `apps/blog/` and modify `apps.py` like this:

**python**
from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'


Add the app to `INSTALLED_APPS` in `config/settings/base.py`:

**python**
INSTALLED_APPS = [
    # ...
    'apps.blog',
]


---

## 🗂️ Project Structure Overview

**plaintext**
    
Master/
├── base/
│   └── utils/
│       └── utils.py
├── apps/
│   ├── __init__.py
│   ├── blog/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── tests.py
│   │   └── migrations/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── .env
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── README.md
└── venv/


---

## ⚙️ Settings Management

BrickDjango separates settings by environment:

- `base.py`: Common settings
- `development.py`: For local dev
- `production.py`: For deployment

You can load them using an environment variable in `manage.py` or `wsgi.py`:

**python**
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


---

## 🛠️ Best Practices

- Always create apps via `brickdjango startapp `
- Keep all business logic apps in `apps/`
- Share reusable code via `base/utils/`
- Commit a `.env.example` for environment variables
- Use separate settings for dev and prod

---

## 🧰 Troubleshooting

### 🔸 Error: "Destination directory does not exist"

Make sure `apps/` exists:

**bash**
mkdir -p apps
brickdjango startapp blog


### 🔸 Error: "App already exists"

Choose another app name or remove the existing folder.


---

BrickDjango gives you a strong foundation to build scalable, maintainable Django applications with ease. Whether you're prototyping or building for production, its modular architecture keeps your code clean and your workflow efficient.

We hope BrickDjango helps you build amazing things — one brick at a time. 🧱✨