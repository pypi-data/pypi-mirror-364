import os
import subprocess
import pkg_resources
import requests

def update_all_packages():
    print("🔄 Checking for outdated packages...")
    outdated = subprocess.run(["pip", "list", "--outdated", "--format=freeze"], capture_output=True, text=True)
    lines = outdated.stdout.strip().split("\n")
    total = len(lines)
    for idx, line in enumerate(lines, 1):
        pkg_name = line.split("==")[0]
        print(f"[{idx}/{total}] Updating {pkg_name}...", end=" ")
        result = subprocess.run(["pip", "install", "--upgrade", pkg_name], capture_output=True)
        print("✅" if result.returncode == 0 else "❌")

def generate_requirements():
    with open("requirements.txt", "w") as f:
        for dist in pkg_resources.working_set:
            f.write(f"{dist.project_name}=={dist.version}\n")
    print("✅ requirements.txt generated.")

def clean_requirements_versions():
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found.")
        return
    with open("requirements.txt") as f:
        lines = f.readlines()
    with open("requirements.txt", "w") as f:
        for line in lines:
            f.write(line.split("==")[0] + "\n")
    print("✅ Versions removed from requirements.txt.")

def update_from_requirements():
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found.")
        return
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    print("✅ Updated from requirements.txt.")

def install_new_package():
    name = input("🔍 Enter a package name: ")
    print("🔎 Searching PyPI...")
    resp = requests.get(f"https://pypi.org/search/?q={name}", headers={"Accept": "application/vnd.pypi.simple.v1+json"})
    if resp.status_code != 200:
        print("❌ Failed to fetch package list.")
        return
    results = resp.json().get("projects", [])
    if not results:
        print("❌ No packages found.")
        return
    for i, pkg in enumerate(results[:10], 1):
        print(f"{i}. {pkg['name']} - {pkg['description']}")
    try:
        choice = int(input("🎯 Choose a package to install: ")) - 1
        pkg_name = results[choice]['name']
        subprocess.run(["pip", "install", pkg_name])
    except Exception:
        print("❌ Invalid choice.")

def main():
    while True:
        print("\n=== UpdatePkgs Menu ===")
        print("1. Update all installed packages")
        print("2. Generate requirements.txt")
        print("3. Remove versions from requirements.txt")
        print("4. Update using requirements.txt")
        print("5. Install new package (with search)")
        print("0. Exit")
        choice = input("Select option: ")
        if choice == "1":
            update_all_packages()
        elif choice == "2":
            generate_requirements()
        elif choice == "3":
            clean_requirements_versions()
        elif choice == "4":
            update_from_requirements()
        elif choice == "5":
            install_new_package()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()