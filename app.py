from flask import Flask, render_template, request, redirect
from datetime import datetime
import json
import os
from datetime import datetime

app = Flask(__name__)
TIEDOSTO = "saatiedot.json"

class Lampotila:
    def __init__(self, lat, lon, lampotila, huomio, paivays):
        self.lat = lat
        self.lon = lon
        self.lampotila = lampotila
        self.huomio = huomio
        self.paivays = paivays

    def to_dict(self):
        return {
            "lat": self.lat,
            "lon": self.lon,
            "lampotila": self.lampotila,
            "huomio": self.huomio,
            "paivays": self.paivays
        }

class Saatiedot:
    def __init__(self):
        self.tiedot = []

    def lisaa_tiedot(self, saatieto):
        self.tiedot.append(saatieto)

    def tallenna_json(self):
        with open(TIEDOSTO, 'w') as f:
            json.dump([s.to_dict() for s in self.tiedot], f, indent=4)

    def lue_json(self):
        if os.path.exists(TIEDOSTO):
            with open(TIEDOSTO, 'r') as f:
                data = json.load(f)
                self.tiedot = [Lampotila(**d) for d in data]
        return self.tiedot

@app.route("/")
def index():
    default_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M")  # Nykyinen päivämäärä ja aika
    return render_template("index.html", default_datetime=default_datetime)

from datetime import datetime


@app.route("/lisaa", methods=["POST"])
def lisaa():
    lat = float(request.form["lat"])
    lon = float(request.form["lon"])
    lampotila = float(request.form["lampotila"])
    huomio = request.form["huomio"]
    
    paivays = request.form["datetime"]  # Käyttäjän syöttämä aika
    paivays = datetime.strptime(paivays, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")


    saatiedot = Saatiedot()
    saatiedot.lue_json()
    saatiedot.lisaa_tiedot(Lampotila(lat, lon, lampotila, huomio, paivays))
    saatiedot.tallenna_json()
    
    return redirect("/lista")


@app.route("/lista")
def lista():
    saatiedot = Saatiedot()
    tiedot = saatiedot.lue_json()

    date_filter = request.args.get("date")
    lat_filter = request.args.get("lat")
    lon_filter = request.args.get("lon")
    huomio_filter = request.args.get("huomio")
    temp_filter = request.args.get("temp")

    if date_filter:
        tiedot = [s for s in tiedot if s.paivays.startswith(date_filter)]
    
    if lat_filter:
        tiedot = [s for s in tiedot if float(s.lat) == float(lat_filter)]
    
    if lon_filter:
        tiedot = [s for s in tiedot if float(s.lon) == float(lon_filter)]
    
    if huomio_filter:
        tiedot = [s for s in tiedot if huomio_filter.lower() in s.huomio.lower()]
    
    if temp_filter:
        tiedot = [s for s in tiedot if float(s.lampotila) == float(temp_filter)]

    tiedot = sorted(tiedot, key=lambda s: datetime.strptime(s.paivays, "%Y-%m-%d %H:%M:%S"), reverse=True)


    return render_template("list.html", tiedot=tiedot)
    
if __name__ == "__main__":
    app.run(debug=True)
