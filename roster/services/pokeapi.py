import random

import requests


class PokeAPIError(Exception):
    pass


POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
REQUEST_TIMEOUT = 10


def _get_json(url: str) -> dict:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PokeAPIError("No se pudo conectar con PokeAPI.") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise PokeAPIError("PokeAPI devolvió una respuesta inválida.") from exc


def get_random_pokemon_by_type(pokemon_type: str) -> dict:
    type_url = f"{POKEAPI_BASE_URL}/type/{pokemon_type}/"
    type_payload = _get_json(type_url)

    pokemon_entries = type_payload.get("pokemon", [])
    if not pokemon_entries:
        raise PokeAPIError("No se encontraron Pokémon para ese tipo.")

    selected_entry = random.choice(pokemon_entries)
    pokemon_url = selected_entry["pokemon"]["url"]

    pokemon_payload = _get_json(pokemon_url)
    return normalize_pokemon_payload(pokemon_payload)


def normalize_pokemon_payload(payload: dict) -> dict:
    stats_map = {
        stat_item["stat"]["name"]: stat_item["base_stat"]
        for stat_item in payload.get("stats", [])
    }

    type_items = sorted(
        payload.get("types", []),
        key=lambda item: item["slot"],
    )
    type_names = [item["type"]["name"] for item in type_items]

    image_url = (
        payload.get("sprites", {})
        .get("other", {})
        .get("official-artwork", {})
        .get("front_default")
    )
    sprite_url = payload.get("sprites", {}).get("front_default", "")

    if not payload.get("id") or not payload.get("name") or not image_url:
        raise PokeAPIError("La respuesta de PokeAPI llegó incompleta.")

    required_stats = [
        "hp",
        "attack",
        "defense",
        "special-attack",
        "special-defense",
        "speed",
    ]
    if any(stat_name not in stats_map for stat_name in required_stats):
        raise PokeAPIError("Faltan stats obligatorios en la respuesta de PokeAPI.")

    return {
        "external_id": payload["id"],
        "name": payload["name"],
        "image_url": image_url,
        "sprite_url": sprite_url or image_url,
        "primary_type": type_names[0],
        "secondary_type": type_names[1] if len(type_names) > 1 else None,
        "hp": stats_map["hp"],
        "attack": stats_map["attack"],
        "defense": stats_map["defense"],
        "special_attack": stats_map["special-attack"],
        "special_defense": stats_map["special-defense"],
        "speed": stats_map["speed"],
        "is_default": payload.get("is_default", True),
    }