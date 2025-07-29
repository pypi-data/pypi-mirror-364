from .generateur import generer_etudiants

def main():
    print("📋 Liste d'étudiants générés automatiquement :\n")
    etudiants = generer_etudiants(10)
    for e in etudiants:
        print(e)
