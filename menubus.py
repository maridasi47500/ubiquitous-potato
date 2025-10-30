import yaml
import random

# Menu des séances
menu_bus = {
    "zen_fluidite": {
        "nom": "Zen et Fluidité",
        "musique": "playlist chill ou ambient",
        "lumiere": "bleu doux",
        "directions": ["gauche"],
        "motivations": [
            "Respire profondément", "Laisse le mouvement te guider", "Tu es en harmonie"
        ],
        "nombre_max_tours": 20,
        "duree_phase": 10,
        "pas_tours": 2
    },
    "challenge_express": {
        "nom": "Challenge Express",
        "musique": "playlist cardio boost",
        "lumiere": "flash intense",
        "directions": ["droite", "gauche"],
        "motivations": [
            "Accélère", "C’est le sprint final", "Donne tout maintenant"
        ],
        "nombre_max_tours": 30,
        "duree_phase": 5,
        "pas_tours": 5
    },
    "bus_duo": {
        "nom": "Séance En Duo",
        "musique": "playlist duo dynamique",
        "lumiere": "double flash",
        "directions": ["droite", "gauche"],
        "motivations": [
            "Fais équipe avec ton partenaire", "Synchronisez vos mouvements", "Un pour tous, tous pour un"
        ],
        "nombre_max_tours": 20,
        "duree_phase": 10,
        "pas_tours": 2
    }
}

# Fonction principale
def generer_bus_yaml(theme):
    params = menu_bus[theme]

    bus = {
        "metadata": {
            "name": f"bus hula hoop - {params['nom']}",
            "description": f"Seance guidee avec theme {params['nom']}, musique et lumiere adapte"
        },
        "automations": {
            "starters": [
                {
                    "type": "assistant.event.OkGoogle",
                    "eventData": "query",
                    "is": f"demarrer bus hula hoop {params['nom']}"
                }
            ],
            "actions": []
        }
    }

    # Accueil
    bus["automations"]["actions"].extend([
        {
            "type": "assistant.command.OkGoogle",
            "okGoogle": f"repete apres moi Bienvenue dans ta bus {params['nom']}",
            "devices": "Jardin de devant - Jardin de devant"
        },
        {
            "type": "assistant.command.OkGoogle",
            "okGoogle": f"joue {params['musique']} sur spotify",
            "devices": "Jardin de devant - Jardin de devant"
        },
        {
            "type": "device.command.ActivateScene",
            "activate": "true",
            "devices": f"en mode {params['lumiere']}"
        }
    ])

    # Boucle de mouvements
    for tours in range(3, params["nombre_max_tours"] + 1, params["pas_tours"]):
        for direction in params["directions"]:
            message_direction = f"Tourne vers {direction} pour {tours} tours"
            if "gauche" in direction:
                message_direction += " meme si c est plus difficile a gauche, tu peux y arriver"

            message_motivation = random.choice(params["motivations"])

            bus["automations"]["actions"].extend([
                {
                    "type": "assistant.command.OkGoogle",
                    "okGoogle": f"repete apres moi {message_direction}",
                    "devices": "Jardin de devant - Jardin de devant"
                },
                {
                    "type": "assistant.command.OkGoogle",
                    "okGoogle": f"repete apres moi {message_motivation}",
                    "devices": "Jardin de devant - Jardin de devant"
                },
                {
                    "type": "assistant.command.OkGoogle",
                    "okGoogle": f"compter de 1 a {tours}",
                    "devices": "Jardin de devant - Jardin de devant"
                },
                {
                    "type": "assistant.command.OkGoogle",
                    "okGoogle": f"attendre {params['duree_phase']} secondes",
                    "devices": "Jardin de devant - Jardin de devant"
                },
                {
                    "type": "device.command.ActivateScene",
                    "activate": "true",
                    "devices": "en mode flash"
                }
            ])

    # Fin de séance
    bus["automations"]["actions"].extend([
        {
            "type": "assistant.command.OkGoogle",
            "okGoogle": "repete apres moi Seance terminee bravo",
            "devices": "Jardin de devant - Jardin de devant"
        },
        {
            "type": "assistant.command.OkGoogle",
            "okGoogle": "arrete la musique",
            "devices": "Jardin de devant - Jardin de devant"
        },
        {
            "type": "assistant.command.OkGoogle",
            "okGoogle": "eteins la lampe",
            "devices": "Jardin de devant - Jardin de devant"
        }
    ])

    # Sauvegarde
    nom_fichier = f"bus_hula_hoop_{theme}.yaml"
    with open(nom_fichier, "w", encoding="utf-8") as fichier:
        yaml.dump(bus, fichier, sort_keys=False)

    print(f"✅ Fichier YAML '{nom_fichier}' cree avec succes pour le theme '{params['nom']}'")

# Exemple d'utilisation
if __name__ == "__main__":
    print("Choisis ton theme :")
    for key, val in menu_bus.items():
        print(f"- {key} : {val['nom']}")
    
    choix = input("Tape le nom du theme (ex: zen_fluidite) : ").strip()
    if choix in menu_bus:
        generer_bus_yaml(choix)
    else:
        print("❌ Theme invalide. Relance le script et choisis parmi les options.")

