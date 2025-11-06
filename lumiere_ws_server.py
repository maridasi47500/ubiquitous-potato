import asyncio
import json
import websockets
import flux_led
import sqlite3

led = flux_led.WifiLedBulb("192.168.1.16")



def get_etapes_from_db(style_name):
    conn = sqlite3.connect("seances.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM effets_lumineux WHERE nom = ?", (style_name,))
    row = cursor.fetchone()
    if not row:
        return []
    effet_id = row[0]
    cursor.execute("""
        SELECT type, valeur
        FROM effet_etapes
        WHERE effet_id = ?
        ORDER BY id ASC
    """, (effet_id,))
    etapes = cursor.fetchall()
    conn.close()
    return etapes

async def effet_lumiere(style):
    etapes = get_etapes_from_db(style)
    for type, valeur in etapes:
        if type == "action":
            print(json.loads(valeur))
            print("=")
            print("turn_on")
            print(json.loads(valeur) == "turn_on")
            if json.loads(valeur) == "turn_on":
                led.turnOn()

            elif json.loads(valeur) == "turn_off":
                led.turnOff()
        elif type == "color":
            r=json.loads(valeur)["r"]
            g=json.loads(valeur)["g"]
            b=json.loads(valeur)["b"]
            led.setRgb(r, g, b, brightness=100)
        elif type == "pause":
            try:
                await asyncio.sleep(int(json.loads(valeur)))
            except:
                await asyncio.sleep(float(json.loads(valeur)))


async def handler(websocket):
    async for message in websocket:
        print(f"💡 Reçu : {message}")
        await effet_lumiere(message)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("🚀 Serveur WebSocket Lumière lancé sur le port 8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

