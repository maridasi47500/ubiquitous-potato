import yaml
from lumiere_controller import run_lumiere
import multiprocessing
import json
from random import randint


import time
from gtts import gTTS
import random
import flux_led
import pychromecast
import asyncio
import websockets
import threading
from dbbus import get_all_bus



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



async def envoyer_lumiere(style):
    uri = "ws://192.168.1.18:8765"  # IP du serveur WebSocket
    async with websockets.connect(uri) as websocket:
        await websocket.send(style)


def envoyer_lumiere_thread(style):
    def run():
        asyncio.run(envoyer_lumiere(style))
    threading.Thread(target=run).start()
def generer_message_vocal(tours, direction, motivations):
    texte = f"\n {tours} tours vers {direction}, "
    if "gauche" in direction:
        #texte += " Même si c’est plus difficile à gauche, tu peux y arriver, "
        texte += " tu peux y arriver, "
    texte += f" {random.choice(motivations)}, "
    speed=str(randint(100, 200)) #
    #texte += "<prosody rate=\""+speed+"%\">"+", ".join(str(n) for n in range(1, tours + 1)) + ",</prosody>"
    texte +=", ".join(str(n) for n in range(1, tours + 1))+","
    return texte




# Initialisation Chromecast
chromecasts, browser = pychromecast.get_chromecasts()
cast = next((cc for cc in chromecasts if cc.name == "Jardin de devant"), None)
if cast is None:
    print("❌ Aucun Chromecast nommé 'Jardin de devant' trouvé.")
    exit(1)

cast.wait()
mc = cast.media_controller
mcradio = cast.media_controller
#mcradio.play_media(url, 'audio/mp3', stream_type='LIVE')
#mcradio.block_until_active()


# Initialisation LED
led = flux_led.WifiLedBulb("192.168.1.12")  # IP de l’ampoule LED
def wait_until_seconds(media_controller, seconds):
    """
    Attend que le média soit en lecture pendant un nombre de secondes donné.
    """
    x = 0
    mytime = 0.5

    while True:
        media_controller.update_status()
        state = media_controller.status.player_state
        #print("🎧 État du média :", state)

        if state == "PAUSED":
            #print("⏹️ Média déjà en pause.")
            break

        if state == "IDLE":
            #print("⏹️ Média arrêté prématurément.")
            break

        if state == "PLAYING":
            x += mytime
            if x >= seconds:
                #print("⏳ Durée écoulée, mise en pause.")
                media_controller.pause()
                break

        time.sleep(mytime)



def wait_until_media_finished(media_controller):
    """
    Wait until the current media finishes playing.
    """
    while True:
        # Update the media controller status
        media_controller.update_status()
        # Check if the media is idle (finished playing)
        #print("etat du media", media_controller.status.player_state)
        time.sleep(0.5)
        # Wait a short time before checking again
        if media_controller.status.player_state == "IDLE":
            print("media termine")
            break



# Menu des séances
def charger_bus_depuis_db():
    rows = get_all_bus()
    bus = {}
    for row in rows:
        theme = row[1]
        try:
            bus[theme] = {
                "id": row[0],

                "theme": row[1],
                "nom": row[2],
                "musique": row[3],
                "lumiere": row[4],
                "directions": nettoyer_json_embedded(row[5]),
                "motivations": nettoyer_json_embedded(row[6]),
                "nombre_max_tours": row[7],
                "duree_phase": row[8],
                "pas_tours": row[9],
                "repetitions": row[10],
                "nombre_minimum_tours": row[11]
            }
        except:
            bus[theme] = {
                "id": row[0],

                "theme": row[1],
                "nom": row[2],
                "musique": row[3],
                "lumiere": row[4],
                "directions": json.loads(row[5]),
                "motivations": json.loads(row[6]),
                "nombre_max_tours": row[7],
                "duree_phase": row[8],
                "pas_tours": row[9],
                "repetitions": row[10],
                "nombre_minimum_tours": row[11]
            }
    return bus

menu_bus = charger_bus_depuis_db()

#menu_bus = {
#    "eveil_matinal": {
#        "nom": "Éveil Matinal",
#        "musique": "https://example.com/morning_energy.mp3",
#        "lumiere": "jaune chaleureux",
#        "directions": ["droite"],
#        "motivations": [
#            "Commence ta journée avec énergie", "Active ton corps", "Rayonne dès le matin"
#        ],
#        "nombre_max_tours": 15,
#        "duree_phase": 8,
#        "pas_tours": 3,
#        "repetitions": 2
#    },
#    "serenite_nocturne": {
#        "nom": "Sérénité Nocturne",
#        "musique": "https://example.com/night_relaxation.mp3",
#        "lumiere": "violet apaisant",
#        "directions": ["gauche"],
#        "motivations": [
#            "Relâche toutes les tensions", "Prépare-toi au repos", "Ton calme est ta force"
#        ],
#        "nombre_max_tours": 10,
#        "duree_phase": 12,
#        "pas_tours": 2,
#        "repetitions": 1
#    },
#
#
#    "zen_fluidite": {
#        "nom": "Zen et Fluidité",
#        "musique": "https://stunnel1.cyber-streaming.com:9162/stream?",
#        "lumiere": "bleu doux",
#        "directions": ["gauche"],
#        "motivations": [
#            "Respire profondément", "Laisse le mouvement te guider", "Tu es en harmonie"
#        ],
#        "nombre_max_tours": 20,
#        "duree_phase": 10,
#        "repetitions": 2,
#        "pas_tours": 2
#    },
#    "challenge_express": {
#        "nom": "Challenge Express",
#        "musique": "https://stunnel1.cyber-streaming.com:9162/stream",
#        "lumiere": "flash intense",
#        "directions": ["droite", "gauche"],
#        "motivations": [
#            "Accélère", "C’est le sprint final", "Donne tout maintenant"
#        ],
#        "nombre_max_tours": 30,
#        "duree_phase": 5,
#        "repetitions": 3,
#        "pas_tours": 5
#    },
#    "bus_duo": {
#        "nom": "Séance En Duo",
#        "musique": "https://example.com/duo_dynamique.mp3",
#        "lumiere": "double flash",
#        "directions": ["droite", "gauche"],
#        "motivations": [
#            "Fais équipe avec ton partenaire", "Synchronisez vos mouvements", "Un pour tous, tous pour un"
#        ],
#        "nombre_max_tours": 20,
#        "duree_phase": 10,
#        "repetitions": 2,
#        "pas_tours": 2
#    }
#}


def effet_lumiere(style):
    if style == "bleu doux":
        led.setRgb(0, 0, 255)
    elif style == "flash intense":
        for _ in range(5):
            led.turnOn()
            led.setRgb(255, 255, 255,brightness=100)
            led.turnOff()
    elif style == "double flash":
        for _ in range(2):
            led.turnOn()
            led.setRgb(255, 255, 0)
            led.turnOff()
def jouer_une_musique(mc, url, media_loaded=False):
    if not media_loaded:
        #print("Chargement du média...")
        mc.play_media(url, 'audio/mp3', stream_type='LIVE')
        mc.block_until_active()

        media_loaded = True
    print("Lecture...")

    mc.play()
    return mc


def jouer_musique(url):
    print("musique------")
    mc.play_media(url, 'audio/mp3')
    mc.block_until_active()
    mc.play()

def arreter_musique():
    mc.stop()

# Fonction principale
def generer_bus_yaml(theme,randomlist="0"):
    menu_bus = charger_bus_depuis_db()
    params = menu_bus[theme]
    print(params)
   
    #dire(f"bienvenue à {params['nom']}")
    print(f"\n🎵 Lecture de la musique : {params['musique']}")
    url=params["musique"]
    #mcradio.play_media(params['musique'], 'audio/mp3')



    print(f"💡 Effet lumière : {params['lumiere']}")
    #asyncio.run(envoyer_lumiere(params["lumiere"]))
    envoyer_lumiere_thread(params["lumiere"])

    for _ in range(params["repetitions"]):
        y=list(range(params["nombre_minimum_tours"], params["nombre_max_tours"] + 1, params["pas_tours"]))
        if randomlist == "1":
            random.shuffle(y)
        for tours in y:
            envoyer_lumiere_thread("flash intense")
    
            print("before state of radio is :  "+str(params['duree_phase'])+" seconds statut mcradio:", mcradio.status.player_state)
            if mcradio.status.player_state == "IDLE":
                mcradio.play_media(params['musique'], 'audio/mp3', stream_type='LIVE')
                mcradio.block_until_active()
                mcradio.play()
                wait_until_seconds(mcradio,int(params['duree_phase']))
                print("after "+str(params['duree_phase'])+" seconds statut mcradio:", mcradio.status.player_state)
            elif mcradio.status.player_state == "PAUSED":
                print("hey")
                mcradio.play()
                wait_until_seconds(mcradio,int(params['duree_phase']))
                print("after "+str(params['duree_phase'])+" seconds statut mcradio:", mcradio.status.player_state)
            else:
                mcradio.play_media(params['musique'], 'audio/mp3', stream_type='LIVE')
                mcradio.block_until_active()
                mcradio.play()
                wait_until_seconds(mcradio,int(params['duree_phase']))
                print("after "+str(params['duree_phase'])+" seconds statut mcradio:", mcradio.status.player_state)
    
            #mcradio.pause()
    
            d=list(params["directions"])
            if randomlist == "1":
                random.shuffle(d)
            for direction in d:
                mytext=""
                print(f"\n➡️ {tours} tours vers {direction}")
                mytext = generer_message_vocal(tours, direction, params['motivations'])
    # Génération du message vocal
                tts = gTTS(mytext, lang='fr')
                tts.save("message.mp3")
                # Diffusion du message
                mc.play_media("http://192.168.1.18:8000/message.mp3", "audio/mp3")  # Remplace par l’URL accessible depuis ton réseau
                mc.block_until_active()
                mc.play()
                wait_until_media_finished(mc)
                time.sleep(0.5)







    msgfin=("Séance terminée ! Bravo")
    print(msgfin)
    tts = gTTS(msgfin, lang='fr')
    tts.save("message.mp3")
    
    # Diffusion du message
    mc.play_media("http://192.168.1.18:8000/message.mp3", "audio/mp3")  # Remplace par l’URL accessible depuis ton réseau
    mc.block_until_active()
    mc.play()
    wait_until_media_finished(mc)
    time.sleep(0.1)

    arreter_musique()
    led.turnOff()


    # YAML export
    nom_fichier = f"bus_hula_hoop_{theme}.yaml"
    with open(nom_fichier, "w", encoding="utf-8") as fichier:
        yaml.dump({"theme": theme, "params": params}, fichier, sort_keys=False)
    print(f"✅ Fichier YAML '{nom_fichier}' créé avec succès")

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

