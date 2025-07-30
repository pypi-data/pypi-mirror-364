import os
import subprocess
import pkg_resources
import requests

def update_all_packages():
    """Update all installed packages to their latest versions."""
    print("🔄 Checking for outdated packages...")
    result = subprocess.run(["pip", "list", "--outdated", "--format=freeze"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")

    if not lines or lines == ['']:
        print("✅ All packages are up to date.")
        return

    total = len(lines)
    for idx, line in enumerate(lines, 1):
        pkg_name = line.split("==")[0]
        print(f"[{idx}/{total}] Updating {pkg_name}...", end=" ")
        upgrade_result = subprocess.run(["pip", "install", "--upgrade", pkg_name], capture_output=True)
        print("✅" if upgrade_result.returncode == 0 else f"❌ ({upgrade_result.stderr.decode().strip()})")

def generate_requirements():
    """Generate a requirements.txt file with pinned package versions."""
    with open("requirements.txt", "w") as f:
        for dist in sorted(pkg_resources.working_set, key=lambda x: x.project_name.lower()):
            f.write(f"{dist.project_name}=={dist.version}\n")
    print("✅ requirements.txt has been generated.")

def clean_requirements_versions():
    """Remove version numbers from the requirements.txt file."""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found.")
        return

    with open("requirements.txt") as f:
        lines = f.readlines()

    with open("requirements.txt", "w") as f:
        for line in lines:
            package = line.split("==")[0].strip()
            if package:
                f.write(package + "\n")
    print("✅ Version numbers removed from requirements.txt.")

def update_from_requirements():
    """Update installed packages based on requirements.txt."""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found.")
        return

    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    print("✅ Packages installed/updated from requirements.txt.")

def install_new_package():
    """Search and install a new package from PyPI."""
    name = input("🔍 Enter a package name to search: ").strip()
    if not name:
        print("❌ Package name cannot be empty.")
        return

    print("🔎 Searching PyPI...")
    resp = requests.get(
        f"https://pypi.org/search/?q={name}",
        headers={"Accept": "application/vnd.pypi.simple.v1+json"}
    )

    if resp.status_code != 200:
        print("❌ Failed to fetch package list from PyPI.")
        return

    results = resp.json().get("projects", [])
    if not results:
        print("❌ No packages found.")
        return

    print("\n📦 Search Results:")
    for i, pkg in enumerate(results[:10], 1):
        print(f"{i}. {pkg['name']} - {pkg.get('description', 'No description available')}")

    try:
        choice = int(input("🎯 Choose a package to install (1-10): ")) - 1
        if not (0 <= choice < len(results)):
            raise ValueError
        selected_pkg = results[choice]['name']
        subprocess.run(["pip", "install", selected_pkg])
        print(f"✅ {selected_pkg} installed.")
    except Exception:
        print("❌ Invalid choice or installation failed.")

def main():
    while True:
        print("\n=== UpdatePkgs Menu ===")
        print("1. Update all installed packages")
        print("2. Generate requirements.txt")
        print("3. Remove versions from requirements.txt")
        print("4. Update using requirements.txt")
        print("5. Install new package (with search)")
        print("0. Exit")

        choice = input("Select an option: ").strip()

        match choice:
            case "1":
                update_all_packages()
            case "2":
                generate_requirements()
            case "3":
                clean_requirements_versions()
            case "4":
                update_from_requirements()
            case "5":
                install_new_package()
            case "0":
                print("👋 Exiting. Goodbye!")
                break
            case _:
                print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
