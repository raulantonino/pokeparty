# Pokeparty

Pokeparty es una aplicación web construida con Django que permite capturar, ordenar y optimizar una party Pokémon usando datos reales obtenidos desde PokeAPI.

El proyecto fue desarrollado como un challenge técnico, con foco en una arquitectura clara, backend sólido, buenas prácticas y una interfaz visual cuidada.

## Demo funcional del proyecto

La aplicación permite:

- seleccionar un tipo de Pokémon desde un grid visual
- capturar un Pokémon random de ese tipo usando PokeAPI
- evitar duplicados dentro de la colección actual
- enviar automáticamente a Party o PC Box según disponibilidad
- ordenar Party y PC Box por distintos criterios
- optimizar el mejor equipo posible
- liberar Pokémon desde Party o PC Box
- promover automáticamente el mejor Pokémon de Box a Party cuando corresponde

## Stack

- Python
- Django
- SQLite
- Requests
- python-dotenv
- PokeAPI

## Arquitectura general

El proyecto está construido como una app SSR con Django Templates + ORM.

### Decisiones principales

- **No se usa DRF en la v1**  
  El proyecto consume una API externa, pero no necesita exponer una API propia.

- **Una sola app principal (`roster`)**  
  El dominio del proyecto está suficientemente concentrado como para mantener una estructura simple y clara.

- **Lógica en capas**
  - `views.py`: coordinación HTTP
  - `services/pokeapi.py`: integración con PokeAPI
  - `services/roster.py`: reglas del negocio
  - `models.py`: persistencia y helpers del dominio

- **Modelos principales**
  - `Pokemon`: ficha base normalizada
  - `RosterEntry`: presencia actual del Pokémon en Party o Box

## Reglas del proyecto

- No se permiten duplicados.
- La Party tiene un máximo de 6 Pokémon.
- Los excedentes van a la PC Box.
- `total_power` se calcula usando los 6 base stats:
  - HP
  - Attack
  - Defense
  - Special Attack
  - Special Defense
  - Speed
- Se puede liberar un Pokémon desde Party o Box.
- Si se libera desde Party y hay Pokémon en la Box, sube automáticamente el más fuerte de la Box.
- Party y Box pueden ordenarse por separado.

## Criterios de ordenamiento

Cada sección puede ordenarse de forma independiente por:

- Inicial
- HP
- ATK
- DEF
- SPE
- Total

## Algoritmo de optimización

El botón **Mejor equipo posible** reorganiza Party y PC Box usando esta lógica:

1. mayor `total_power`
2. mejor diversidad de tipos en la Party
3. mayor stat dominante
4. mayor speed
5. menor `external_id`

Esto permite una optimización consistente y determinística.

## Diseño visual

La interfaz busca una mezcla de:

- estética Pokémon
- retro-tech / Y2K
- un toque leve tipo Digimon / interfaces de principios de los 2000
- glassmorphism moderado

El objetivo fue lograr una UI clara, usable y con personalidad, sin sacrificar legibilidad.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/raulantonino/pokeparty.git
cd pokeparty
```

### 2. Crear y activar entorno virtual

En Windows PowerShell:

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto usando `.env.example` como referencia.

Ejemplo:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

## Ejecución local

### 1. Aplicar migraciones

```bash
python manage.py migrate
```

### 2. Levantar el servidor

```bash
python manage.py runserver
```

La aplicación quedará disponible en:

```text
http://127.0.0.1:8000/
```

## Ejecutar tests

```bash
python manage.py test roster.tests -v 2
```

## Estructura base

```text
pokeparty/
├─ config/
├─ docs/
├─ roster/
│  ├─ services/
│  └─ tests/
├─ static/
├─ templates/
├─ .env.example
├─ manage.py
└─ requirements.txt
```

## Buenas prácticas aplicadas

- decisiones técnicas documentadas
- vistas delgadas
- separación entre integración externa y lógica del dominio
- restricciones importantes en el modelo
- manejo de errores de API
- tests de modelos, servicios y vistas
- UI responsive desde la base

## Mejoras futuras posibles

- filtros adicionales por tipo en Party y Box
- comparación más explícita entre Pokémon
- badges visuales para stat dominante
- paginación o búsqueda si la Box crece mucho
- deploy en producción
- cobertura de tests más amplia
- animaciones microinteractivas adicionales

## Estado actual

Proyecto funcional y en estado sólido de portafolio.
