"""Read the supplied CSV export and produce small Pokédex records for the UI."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        yield from csv.DictReader(file)


class PokedexData:
    def __init__(self, directory: Path, art_dir: Path):
        self.directory, self.art_dir = directory, art_dir
        self.is_ready = directory.exists()
        self.candidates: list[dict] = []
        if self.is_ready:
            self._load()

    def _load(self):
        self.names = {row["ndex_id"]: row for row in rows(self.directory / "ndex_names.csv")}
        self.types = {row["id"]: row["name"] for row in rows(self.directory / "types.csv")}
        self.abilities = {row["id"]: row["name"] for row in rows(self.directory / "abilities.csv")}
        self.forms = {row["id"]: row for row in rows(self.directory / "pokemon_forms.csv")}
        self.default_forms = {row["ndex_id"]: row for row in self.forms.values() if row["is_default_form"] == "true"}
        self.by_identifier = {row["identifier"]: row for row in self.default_forms.values()}
        self.evolution_tree = {row["ndex_id"]: row["evolution_tree_id"] for row in rows(self.directory / "ndex_evolution_trees.csv")}
        self.tree_members = defaultdict(list)
        for dex_id, tree in self.evolution_tree.items():
            if dex_id in self.default_forms:
                self.tree_members[tree].append(dex_id)

        self.flavor = {}
        for row in rows(self.directory / "flavor_texts.csv"):
            self.flavor.setdefault(row["pokemon_form_identifier"], row["flavor_text"])

        self.moves = {row["id"]: row for row in rows(self.directory / "moves.csv")}
        self.moves_by_form = defaultdict(list)
        for row in rows(self.directory / "pokemon_moves.csv"):
            if row["version_identifier"] == "scarlet-violet" and row["pokemon_move_method_id"] in {"1", "2", "4"}:
                self.moves_by_form[row["pokemon_form_id"]].append(row)

        image_ids = set()
        if self.art_dir.exists():
            for image in self.art_dir.glob("*.jpg"):
                match = re.match(r"(\d+)", image.stem)
                if match:
                    image_ids.add(match.group(1))
        self.candidates = [
            {"identifier": form["identifier"], "name": self.names[dex_id]["name_english"], "dex_id": dex_id}
            for dex_id, form in self.default_forms.items()
            if dex_id in image_ids
        ]

    def details(self, identifier: str):
        form = self.by_identifier.get(identifier)
        if not form:
            return None
        dex_id = form["ndex_id"]
        name = self.names[dex_id]
        tree = self.evolution_tree.get(dex_id)
        evolution = [
            {"dex_id": member, "name": self.names[member]["name_english"], "identifier": self.default_forms[member]["identifier"]}
            for member in sorted(self.tree_members.get(tree, []), key=int)
        ]
        learned = []
        seen = set()
        for relation in sorted(self.moves_by_form.get(form["id"], []), key=lambda r: (int(r["level"] or 0), r["move_id"])):
            move = self.moves.get(relation["move_id"])
            if move and move["id"] not in seen:
                learned.append({"name": move["name"], "type": self.types.get(move["type_id"], "Unknown"), "power": move["power"] or "—", "level": relation["level"] or "TM / tutor"})
                seen.add(move["id"])
        return {
            "name": name["name_english"], "dex_id": dex_id, "identifier": identifier, "category": form["pokemon_category"],
            "types": [self.types.get(form["type_1_id"]), self.types.get(form["type_2_id"])],
            "height": form["height_m"], "weight": form["weight_kg"], "flavor": self.flavor.get(identifier, "No Pokédex description is available."),
            "abilities": [self.abilities.get(form[key]) for key in ("ability_primary_id", "ability_secondary_id", "ability_hidden_id") if form[key]],
            "stats": [("HP", form["stat_hp"]), ("Attack", form["stat_attack"]), ("Defense", form["stat_defense"]), ("Sp. Atk", form["stat_spatk"]), ("Sp. Def", form["stat_spdef"]), ("Speed", form["stat_speed"])],
            "total": form["stat_total"], "evolution": evolution, "moves": learned[:24], "art": form["main_image_normal_path_medium"],
        }
