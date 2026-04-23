def build_pokemon_data(
    external_id: int,
    *,
    name: str | None = None,
    primary_type: str = "water",
    secondary_type: str | None = None,
    hp: int = 50,
    attack: int = 50,
    defense: int = 50,
    special_attack: int = 50,
    special_defense: int = 50,
    speed: int = 50,
):
    return {
        "external_id": external_id,
        "name": name or f"poke-{external_id}",
        "image_url": f"https://img.test/{external_id}.png",
        "sprite_url": f"https://img.test/{external_id}-sprite.png",
        "primary_type": primary_type,
        "secondary_type": secondary_type,
        "hp": hp,
        "attack": attack,
        "defense": defense,
        "special_attack": special_attack,
        "special_defense": special_defense,
        "speed": speed,
        "is_default": True,
    }


def build_uniform_pokemon_data(
    external_id: int,
    stat_value: int,
    **overrides,
):
    return build_pokemon_data(
        external_id,
        hp=stat_value,
        attack=stat_value,
        defense=stat_value,
        special_attack=stat_value,
        special_defense=stat_value,
        speed=stat_value,
        **overrides,
    )