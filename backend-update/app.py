"""A local image-to-Pokédex web application."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import Flask, abort, render_template, request, send_from_directory

from pokedex_data import PokedexData
from vision import PokemonRecognizer

ROOT = Path(__file__).parent
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

DATA_ROOT = ROOT / "pokemon-database"
data = PokedexData(
    Path(os.environ.get("POKEDEX_DATA_DIR", DATA_ROOT / "data_export_all_csv_comma")),
    Path(os.environ.get("POKEMON_ART_DIR", DATA_ROOT / "archive (1)" / "pokemon_jpg" / "pokemon_jpg")),
)
recognizer = PokemonRecognizer(data.candidates)


@app.get("/")
def home():
    return render_template("index.html", ready=data.is_ready, count=len(data.candidates))


@app.post("/identify")
def identify():
    image = request.files.get("image")
    if not image or not image.filename:
        return render_template("index.html", ready=data.is_ready, count=len(data.candidates), error="Choose an image first."), 400

    suffix = Path(image.filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        return render_template("index.html", ready=data.is_ready, count=len(data.candidates), error="Please upload a JPG, PNG, or WebP image."), 400

    file_name = f"{uuid.uuid4().hex}{suffix}"
    image.save(UPLOAD_DIR / file_name)
    predictions = recognizer.predict(UPLOAD_DIR / file_name)
    if not predictions:
        return render_template("index.html", ready=data.is_ready, count=len(data.candidates), error="The vision model could not identify this image."), 422

    result = data.details(predictions[0]["identifier"])
    return render_template("result.html", result=result, predictions=predictions, upload=file_name)


@app.get("/pokemon/<identifier>")
def pokemon(identifier: str):
    result = data.details(identifier)
    if not result:
        abort(404)
    return render_template("result.html", result=result, predictions=[], upload=None)


@app.get("/uploads/<path:name>")
def upload(name: str):
    return send_from_directory(UPLOAD_DIR, name)


@app.errorhandler(413)
def too_large(_):
    return render_template("index.html", ready=data.is_ready, count=len(data.candidates), error="Images must be 10 MB or smaller."), 413


if __name__ == "__main__":
    app.run(debug=True, port=5001)
