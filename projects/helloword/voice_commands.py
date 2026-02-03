import math
import datetime
import json
import os

class ProgrammeComplet:
    def __init__(self):
        self.historique = []
        self.taches = []
        self.fichier_data = "data.json"
        self.fichier_taches = "taches.json"
        self.charger_donnees()
        self.charger_taches()
    
    def charger_donnees(self):
        """Charger les données depuis un fichier JSON"""
        try:
            if os.path.exists(self.fichier_data):
                with open(self.fichier_data, 'r', encoding='utf-8') as f:
                    self.historique = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur lors du chargement des données: {e}")
            self.historique = []
    
    def charger_taches(self):
        """Charger les tâches depuis un fichier JSON"""
        try:
            if os.path.exists(self.fichier_taches):
                with open(self.fichier_taches, 'r', encoding='utf-8') as f:
                    self.taches = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur lors du chargement des tâches: {e}")
            self.taches = []
    
    def sauvegarder_donnees(self):
        """Sauvegarder les données dans un fichier JSON"""
        try:
            with open(self.fichier_data, 'w', encoding='utf-8') as f:
                json.dump(self.historique, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def sauvegarder_taches(self):
        """Sauvegarder les tâches dans un fichier JSON"""
        try:
            with open(self.fichier_taches, 'w', encoding='utf-8') as f:
                json.dump(self.taches, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des tâches: {e}")
    
    def ajouter_historique(self, operation, resultat):
        """Ajouter une opération à l'historique"""
        entree = {
            'date': str(datetime.datetime.now()),
            'operation': operation,
            'resultat': resultat
        }
        self.historique.append(entree)
        self.sauvegarder_donnees()
    
    # [Le reste du code reste inchangé jusqu'au gestionnaire de tâches...]
    
    def gestionnaire_taches(self):
        """Gestionnaire de tâches simple"""
        print("\n" + "="*50)
        print("GESTIONNAIRE DE TÂCHES")
        print("="*50)
        
        while True:
            print("\n1. Ajouter une tâche")
            print("2. Voir les tâches")
            print("3. Marquer une tâche comme terminée")
            print("4. Supprimer une tâche")
            print("5. Quitter")
            
            choix = input("\nChoisissez une option (1-5): ")
            
            if choix == '1':
                tache = input("Description de la tâche: ")
                self.taches.append({"tache": tache, "terminee": False, "date": str(datetime.datetime.now())})
                self.sauvegarder_taches()
                print("✓ Tâche ajoutée!")
            
            elif choix == '2':
                if not self.taches:
                    print("Aucune tâche.")
                else:
                    print("\nListe des tâches:")
                    for i, t in enumerate(self.taches, 1):
                        status = "✓" if t["terminee"] else "○"
                        date = t.get("date", "Date inconnue")[:16]
                        print(f"{i}. [{status}] {t['tache']} (ajoutée le {date})")
            
            elif choix == '3':
                if self.taches:
                    try:
                        num = int(input("Numéro de la tâche à terminer: ")) - 1
                        if 0 <= num < len(self.taches):
                            self.taches[num]["terminee"] = True
                            self.sauvegarder_taches()
                            print("✓ Tâche marquée comme terminée!")
                        else:
                            print("Numéro invalide")
                    except ValueError:
                        print("Veuillez entrer un nombre")
                else:
                    print("Aucune tâche à marquer")
            
            elif choix == '4':
                if self.taches:
                    try:
                        num = int(input("Numéro de la tâche à supprimer: ")) - 1
                        if 0 <= num < len(self.taches):
                            supprimee = self.taches.pop(num)
                            self.sauvegarder_taches()
                            print(f"✓ Tâche '{supprimee['tache']}' supprimée!")
                        else:
                            print("Numéro invalide")
                    except ValueError:
                        print("Veuillez entrer un nombre")
                else:
                    print("Aucune tâche à supprimer")
            
            elif choix == '5':
                break
            
            else:
                print("Choix invalide!")
    
    # [Le reste du code reste inchangé...]

# Pour installer psutil si nécessaire:
def installer_dependances():
    """Installer les dépendances manquantes"""
    try:
        import psutil
    except ImportError:
        print("Le module psutil n'est pas installé.")
        reponse = input("Voulez-vous l'installer automatiquement? (o/n): ").lower()
        if reponse in ['o', 'oui', 'y', 'yes']:
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
                print("✓ psutil installé avec succès!")
                return True
            except Exception as e:
                print(f"✗ Erreur lors de l'installation: {e}")
                print("Vous pouvez installer manuellement avec: pip install psutil")
                return False
        else:
            print("Les fonctionnalités système seront limitées sans psutil.")
            return False
    return True

def main():
    """Fonction principale"""
    print("Initialisation du programme...")
    
    # Installer psutil si nécessaire
    installer_dependances()
    
    programme = ProgrammeComplet()
    
    try:
        programme.menu_principal()
    except KeyboardInterrupt:
        print("\n\nProgramme interrompu par l'utilisateur.")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
    finally:
        print("\nNettoyage en cours...")
        programme.sauvegarder_donnees()
        programme.sauvegarder_taches()
        print("Données sauvegardées. Au revoir!")

if __name__ == "__main__":
    main()