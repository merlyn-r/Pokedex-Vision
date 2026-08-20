"""Pretrained CLIP zero-shot Pokémon image classification."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


class PokemonRecognizer:
    def __init__(self, candidates: list[dict]):
        self.candidates = candidates
        self._model = None
        self._processor = None

    def _load(self):
        if self._model is not None:
            return
        from transformers import CLIPModel, CLIPProcessor

        self._processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self._model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self._model.eval()

    def predict(self, path: Path, limit: int = 3) -> list[dict]:
        """Return the most likely species. First run downloads the pretrained model."""
        if not self.candidates:
            return []
        self._load()
        import torch

        image = Image.open(path).convert("RGB")
        labels = [f"a picture of {item['name']}, the Pokémon" for item in self.candidates]
        scores = []
        # Batching avoids excessive memory use for the full Pokédex label list.
        for start in range(0, len(labels), 128):
            inputs = self._processor(text=labels[start : start + 128], images=image, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = self._model(**inputs).logits_per_image[0]
            scores.extend(logits.tolist())

        values = torch.tensor(scores)
        probabilities = torch.softmax(values, dim=0)
        top = torch.topk(probabilities, min(limit, len(self.candidates)))
        return [
            {**self.candidates[index], "confidence": round(float(probabilities[index]) * 100, 1)}
            for index in top.indices.tolist()
        ]
