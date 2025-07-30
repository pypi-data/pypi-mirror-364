import sys
from .generator import GeneratorAppMaya


def main():
    if len(sys.argv) < 2:
        print("Usage: generatorappmaya <nom_app> [destination]")
        sys.exit(1)

    app_name = sys.argv[1]
    destination = sys.argv[2] if len(sys.argv) > 2 else None

    generator = GeneratorAppMaya(app_name, destination)
    generator.generate()
    print(f"✅ Application Django '{app_name}' générée avec succès.")
