import subprocess
import ctypes
import sys
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_local_users():
    try:
        result = subprocess.run(["net", "user"], capture_output=True, text=True, encoding="cp850")
        lines = result.stdout.splitlines()
        users = []
        capture = False
        for line in lines:
            if "---" in line:
                capture = not capture
                continue
            if capture and line.strip():
                users.extend(line.split())
        return sorted(users)
    except:
        return []

def change_password(username, new_password):
    result = subprocess.run(
        ["net", "user", username, new_password],
        capture_output=True, text=True, encoding="cp850"
    )
    if result.returncode == 0:
        return True, "Mot de passe change avec succes."
    else:
        err = result.stderr.strip() or result.stdout.strip()
        return False, f"Erreur : {err}"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("=" * 48)
    print("   Changement de mot de passe - Windows")
    print("=" * 48)

def main():
    clear()
    banner()

    if not is_admin():
        print("\n[!] Ce script doit etre execute en tant qu'administrateur.")
        print("    Clic droit > Executer en tant qu'administrateur")
        input("\nAppuyez sur Entree pour quitter...")
        sys.exit(1)

    users = get_local_users()
    if users:
        print("\nUtilisateurs locaux detectes :")
        for i, u in enumerate(users, 1):
            print(f"  {i:>2}. {u}")
    else:
        print("\n[!] Impossible de lister les utilisateurs.")

    print()

    while True:
        username = input("Nom d'utilisateur : ").strip()
        if username:
            break
        print("  [!] Entrez un nom d'utilisateur.")

    print("\n(Les mots de passe sont visibles - fermez la fenetre apres usage)\n")
    while True:
        pw1 = input("Nouveau mot de passe    : ").strip()
        if pw1:
            break
        print("  [!] Le mot de passe ne peut pas etre vide.")

    while True:
        pw2 = input("Confirmer mot de passe  : ").strip()
        if pw2 == pw1:
            break
        print("  [!] Les mots de passe ne correspondent pas. Reessayez.\n")

    print()
    ok, msg = change_password(username, pw1)
    prefix = "[OK]" if ok else "[ERREUR]"
    print(f"{prefix} {msg}")

    input("\nAppuyez sur Entree pour quitter...")

if __name__ == "__main__":
    main()
