import sys
from .checker import is_even

def main():
    if len(sys.argv) != 2:
        print("Usage :math-helper-app' <nombre_entier>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Erreur : veuillez entrer un nombre entier valide.")
        sys.exit(1)

    if is_even(n):
        print(f"{n} est un nombre pair.")
    else:
        print(f"{n} est un nombre impair.")
