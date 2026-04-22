from django.db import models
from django.db.models import ExpressionWrapper, F, IntegerField


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PokemonType(models.TextChoices):
    NORMAL = "normal", "Normal"
    FIRE = "fire", "Fuego"
    WATER = "water", "Agua"
    ELECTRIC = "electric", "Eléctrico"
    GRASS = "grass", "Planta"
    ICE = "ice", "Hielo"
    FIGHTING = "fighting", "Lucha"
    POISON = "poison", "Veneno"
    GROUND = "ground", "Tierra"
    FLYING = "flying", "Volador"
    PSYCHIC = "psychic", "Psíquico"
    BUG = "bug", "Bicho"
    ROCK = "rock", "Roca"
    GHOST = "ghost", "Fantasma"
    DRAGON = "dragon", "Dragón"
    DARK = "dark", "Siniestro"
    STEEL = "steel", "Acero"
    FAIRY = "fairy", "Hada"


class Pokemon(TimeStampedModel):
    external_id = models.PositiveIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)

    image_url = models.URLField()
    sprite_url = models.URLField(blank=True)

    primary_type = models.CharField(
        max_length=20,
        choices=PokemonType.choices,
        db_index=True,
    )
    secondary_type = models.CharField(
        max_length=20,
        choices=PokemonType.choices,
        blank=True,
        null=True,
        db_index=True,
    )

    hp = models.PositiveSmallIntegerField()
    attack = models.PositiveSmallIntegerField()
    defense = models.PositiveSmallIntegerField()
    special_attack = models.PositiveSmallIntegerField()
    special_defense = models.PositiveSmallIntegerField()
    speed = models.PositiveSmallIntegerField()

    is_default = models.BooleanField(default=True)

    class Meta:
        ordering = ["external_id"]

    def __str__(self):
        return f"#{self.external_id} {self.display_name}"

    @property
    def display_name(self):
        return self.name.replace("-", " ").title()

    @property
    def total_power(self):
        return (
            self.hp
            + self.attack
            + self.defense
            + self.special_attack
            + self.special_defense
            + self.speed
        )

    @property
    def dominant_stat_name(self):
        stats = {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "special_attack": self.special_attack,
            "special_defense": self.special_defense,
            "speed": self.speed,
        }
        return max(stats, key=stats.get)

    @property
    def dominant_stat_value(self):
        return getattr(self, self.dominant_stat_name)


class RosterEntryQuerySet(models.QuerySet):
    def with_pokemon(self):
        return self.select_related("pokemon")

    def in_party(self):
        return self.filter(location="party")

    def in_box(self):
        return self.filter(location="box")

    def ordered_for_display(self):
        return self.with_pokemon().order_by("location", "position", "pokemon__external_id")

    def annotate_total_power(self):
        total_power_expression = ExpressionWrapper(
            F("pokemon__hp")
            + F("pokemon__attack")
            + F("pokemon__defense")
            + F("pokemon__special_attack")
            + F("pokemon__special_defense")
            + F("pokemon__speed"),
            output_field=IntegerField(),
        )
        return self.annotate(total_power=total_power_expression)


class RosterEntry(TimeStampedModel):
    class Location(models.TextChoices):
        PARTY = "party", "Party"
        BOX = "box", "PC Box"

    pokemon = models.OneToOneField(
        Pokemon,
        on_delete=models.PROTECT,
        related_name="roster_entry",
    )
    location = models.CharField(
        max_length=10,
        choices=Location.choices,
        db_index=True,
    )
    position = models.PositiveSmallIntegerField()

    objects = RosterEntryQuerySet.as_manager()

    class Meta:
        ordering = ["location", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["location", "position"],
                name="unique_position_per_location",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        location="party",
                        position__gte=1,
                        position__lte=6,
                    )
                    | models.Q(
                        location="box",
                        position__gte=1,
                    )
                ),
                name="valid_position_for_location",
            ),
        ]

    def __str__(self):
        return f"{self.pokemon.display_name} - {self.get_location_display()} #{self.position}"

    @property
    def total_power(self):
        return self.pokemon.total_power