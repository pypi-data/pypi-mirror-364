import os
import sys
import re

EXCLUDED_DIRS = {"venv", "__pycache__", ".git", "migrations", "tests"}

GETENV_PATTERN = re.compile(r"os\.getenv\(\s*[\"']([^\"']+)[\"'](?:\s*,\s*[\"']?([^\"')]+)?[\"']?)?\)")
ENVIRON_PATTERN = re.compile(r"os\.environ\[\s*[\"']([^\"']+)[\"']\s*\]")

def should_scan(file_path):
    return file_path.endswith(".py") and not any(part in EXCLUDED_DIRS for part in file_path.split(os.sep))

def extract_env_variables(root_dir="."):
    env_vars = {}
    scanned_files = 0
    ignored_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if not should_scan(file_path):
                ignored_files.append(file_path)
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # os.getenv("VAR", default)
                    for match in GETENV_PATTERN.finditer(content):
                        name = match.group(1)
                        default = match.group(2) if match.group(2) is not None else ""
                        env_vars[name] = default

                    # os.environ["VAR"]
                    for match in ENVIRON_PATTERN.finditer(content):
                        name = match.group(1)
                        if name not in env_vars:
                            env_vars[name] = ""

                scanned_files += 1
            except Exception as e:
                ignored_files.append(file_path)

    return env_vars, scanned_files, ignored_files

def write_env_files(env_vars):
    if not env_vars:
        print("Aucune variable d'environnement détectée.")
        return

    with open(".env", "w") as f_env, open(".env.example", "w") as f_example:
        for name, value in env_vars.items():
            f_env.write(f"{name}={value}\n")
            f_example.write(f"{name}=\n")

    print("Fichiers .env et .env.example générés.")

def main():
    if len(sys.argv) < 2 or sys.argv[1] != "init":
        print("Usage : dotenv-wizard init [chemin]")
        return

    root_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"Analyse du dossier : {root_dir}")
    env_vars, scanned, ignored = extract_env_variables(root_dir)
    write_env_files(env_vars)

    print("\n Résumé :")
    print(f"  Fichiers scannés     : {scanned}")
    print(f"  Fichiers ignorés     : {len(ignored)}")
    print(f"  Variables détectées  : {len(env_vars)}")
    if env_vars:
        print("  ➤ ", ", ".join(env_vars.keys()))
