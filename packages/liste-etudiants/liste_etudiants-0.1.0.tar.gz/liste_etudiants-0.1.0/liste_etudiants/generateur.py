from faker import Faker
from datetime import date
from .etudiant import Etudiant

fake = Faker('fr_FR')

def generer_etudiants(nb=5):
    etudiants = []
    for _ in range(nb):
        prenom = fake.first_name()
        nom = fake.last_name()
        date_naissance = fake.date_of_birth(minimum_age=18, maximum_age=25)
        age = date.today().year - date_naissance.year
        etudiants.append(Etudiant(nom, prenom, age, date_naissance))
    return etudiants
