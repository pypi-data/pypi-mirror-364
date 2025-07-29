class Etudiant:
    def __init__(self, nom, prenom, age, date_naissance):
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.date_naissance = date_naissance

    def __str__(self):
        return f"{self.prenom} {self.nom} - Âge : {self.age} - Né(e) le : {self.date_naissance}"
