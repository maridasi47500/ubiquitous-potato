import yaml
import json
import random

def nettoyer_json_embedded(data, max_depth=5):
    """Essaie de décoder un JSON encodé plusieurs fois."""
    for _ in range(max_depth):
        if isinstance(data, list):
            return data
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            break
    return data if isinstance(data, list) else []



def generer_yaml_depuis_formulaire(params):
    (
        theme, nom, musique, lumiere_dedans, lumiere_dehors, directions_json, motivations_json,
        nombre_max_tours, duree_phase, nbmintours, popstar
    ) = params

    #directions = json.loads(json.loads(str(directions_json)))
    directions = nettoyer_json_embedded(directions_json)
    motivations = nettoyer_json_embedded(motivations_json)
    print(theme, nom, musique, lumiere_dedans, lumiere_dehors, directions,motivations)

    bus = {
        "metadata": {
            "name": nom,
            "description": f"Voyage en bus '{theme}' avec musique, lumières et messages"
        },
        "automations": {
            "starters": [
                {
                    "type": "assistant.event.OkGoogle",
                    "eventData": "query",
                    "is": f"demarrer bus {theme}"
                }
            ],
            "actions": []
        }
    }

    bus["automations"]["actions"].extend([
        {
            "type": "assistant.command.Broadcast",
            "message": f"Bienvenue dans ton bus {nom}",
            "devices": "Jardin de devant - Jardin de devant"
        },
        {
            "type": "assistant.command.OkGoogle",
            "okGoogle": f"joue {musique}",
            "devices": "Jardin de devant - Jardin de devant"
        },
        {
            "type": "device.command.ActivateScene",
            "activate": "true",
            "devices": f"en mode {lumiere_dehors}"
        }
    ])

    for tours in range(nbmintours, nombre_max_tours + 1, 1):
       for direction in directions:
           message_direction = f"prochain arret {direction}"
           message_motivation = random.choice(motivations)

           bus["automations"]["actions"].extend([
               {
                   "type": "time.delay",
                   "for": f"5sec"
               },
               {
                   "type": "assistant.command.Broadcast",
                   "message": f"{message_direction}",
                   "devices": "Jardin de devant - Jardin de devant"
               },
               {
                   "type": "time.delay",
                   "for": f"5sec"
               },
               {
                   "type": "assistant.command.Broadcast",
                   "message": f"{message_motivation}",
                   "devices": "Jardin de devant - Jardin de devant"
               },
               {
                   "type": "time.delay",
                   "for": f"5sec"
               },

               {
                   "type": "device.command.ActivateScene",
                   "activate": "true",
                   "devices": f"en mode {lumiere_dedans}"
               },
               {
                   "type": "time.delay",
                   "for": f"{duree_phase}sec"
               }
           ])

    bus["automations"]["actions"].extend([
        {
            "type": "time.delay",
            "for": f"5sec"
        },
        {
            "type": "assistant.command.Broadcast",
            "message": f"le bus est arrivé",
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

    nom_fichier = f"bus_{theme}.yaml"
    with open(nom_fichier, "w", encoding="utf-8") as fichier:
        yaml.dump(bus, fichier, sort_keys=False)

    print(f"✅ Fichier YAML '{nom_fichier}' généré avec succès.")

    return nom_fichier  # ← retourne le nom du fichier


