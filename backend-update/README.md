# Vision Pokédex

Upload a Pokémon image, identify its most likely species with a pretrained deep-learning vision model, then display a detailed entry drawn from the supplied CSV export.

## Included details

- Type, category, height, weight, abilities and base stats
- Pokédex flavor text
- Full evolution line
- Scarlet/Violet learnable moves (up to 24 displayed)

## Start it in VS Code

1. Open this `pokedex-vision` folder in VS Code.
2. Create and activate a Python virtual environment.
3. Install the dependencies: `pip install -r requirements.txt`
4. Run: `python app.py`
5. Visit `http://127.0.0.1:5001`.

The defaults already point to your two source folders. If you move either source, set these environment variables before starting:

```bash
export POKEDEX_DATA_DIR="/path/to/data_export_all_csv_comma"
export POKEMON_ART_DIR="/path/to/pokemon_jpg"
```

On the first image upload, the app downloads `openai/clip-vit-base-patch32` from Hugging Face. This is a pretrained vision model, not a model trained on a single reference image per species.

## Recognition scope

The Kaggle artwork archive supplies the candidate list, so recognition is limited to the Pokémon represented there (roughly National Dex 1–721) and is best for clear artwork or character-focused images. For dependable real-world/anime/screenshot recognition, the next upgrade is fine-tuning this model on a labelled multi-image-per-Pokémon dataset.
