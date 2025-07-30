import sys
from .server import run_server

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        run_server()
    else:
        print("Usage: navin runserver") 