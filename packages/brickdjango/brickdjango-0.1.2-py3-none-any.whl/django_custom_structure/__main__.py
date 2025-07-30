import sys
from .project_setup import create_project
from .app_setup import create_app

def main():
    if len(sys.argv) != 3:
        print("Usage:\n  brickdjango startproject <project_name>\n  brickdjango startapp <app_name>")
        sys.exit(1)

    command = sys.argv[1]
    name = sys.argv[2]

    if command == 'startproject':
        create_project(name)
    elif command == 'startapp':
        create_app(name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
