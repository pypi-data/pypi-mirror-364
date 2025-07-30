import sys
from .project_setup import create_project
from .app_setup import create_app
from . import __version__

def main():
    args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help'):
        print("Usage:\n  brickdjango startproject <project_name>\n  brickdjango startapp <app_name>\n  brickdjango --version")
        sys.exit(0)

    if args[0] in ('--version', '-v'):
        print(f"brickdjango version {__version__}")
        sys.exit(0)

    if len(args) != 2:
        print("Error: Invalid arguments.")
        print("Usage:\n  brickdjango startproject <project_name>\n  brickdjango startapp <app_name>")
        sys.exit(1)

    command, name = args

    if command == 'startproject':
        create_project(name)
    elif command == 'startapp':
        create_app(name)
    else:
        print(f"Unknown command: {command}")
        print("Usage:\n  brickdjango startproject <project_name>\n  brickdjango startapp <app_name>")
        sys.exit(1)

if __name__ == "__main__":
    main()
