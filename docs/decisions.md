# Pokeparty - Decisiones del Proyecto

## 1. Contexto del proyecto

- Tipo de proyecto: challenge técnico nuevo (greenfield) con integración de API externa.
- Entregable principal: código + documentación técnica.
- Objetivo principal: construir un proyecto de portafolio en Django, con backend sólido, arquitectura clara, buenas prácticas visibles y una UI cuidada.
- Fuente de verdad: enunciado del challenge + documento de decisiones + código real del proyecto.

## 2. Definición del producto

- La aplicación permite capturar, ordenar y optimizar una party Pokémon usando datos reales obtenidos desde PokeAPI.
- El proyecto usa renderizado server-side con Django Templates.
- No existe frontend separado ni aplicación móvil en la v1.
- No existe sistema de autenticación en la v1.
- No existen subidas de archivos en la v1.

## 3. Reglas principales del negocio

- El usuario captura un Pokémon random a partir de un tipo seleccionado.
- No se permiten Pokémon duplicados en la colección actual.
- La Party puede contener un máximo de 6 Pokémon.
- Los excedentes se envían automáticamente a la PC Box.
- Un Pokémon puede liberarse tanto desde la Party como desde la PC Box.
- Si se libera un Pokémon desde la Party y existen Pokémon en la PC Box, sube automáticamente el Pokémon más fuerte de la Box.
- Si se libera un Pokémon desde la Party y la Box está vacía, la Party simplemente se compacta.
- Si se libera un Pokémon desde la PC Box, la Box se compacta.
- Liberar un Pokémon elimina solo el `RosterEntry` local, no la ficha base normalizada del modelo `Pokemon`.
- Los datos del Pokémon deben persistir en la base de datos local.
- El flujo de “Mejor equipo posible” usa los 6 base stats:
  - hp
  - attack
  - defense
  - special_attack
  - special_defense
  - speed
- Desempates en la optimización:
  1. mayor `total_power`
  2. mejor diversidad de tipos en la Party final
  3. mayor stat individual dominante
  4. mayor speed
  5. menor `external_id` para mantener orden determinístico

## 4. Decisiones de arquitectura

- Estilo de arquitectura: Django SSR + ORM.
- No se usa DRF en la v1.
- API externa: PokeAPI.
- La integración con PokeAPI vive en una capa de servicios dedicada.
- La lógica de roster y optimización vive en una capa de servicios separada.
- Las vistas deben mantenerse delgadas.
- La lógica de consultas repetidas debe ir a QuerySets, managers o servicios.
- La lógica de ordenamiento por `total_power` se resuelve en Python, ya que Party y Box son conjuntos pequeños y no justifica complejidad adicional en ORM para este caso.

## 5. Estructura del proyecto

- Carpeta global de configuración: `config/`
- App principal: `roster`
- Carpeta global de templates: `templates/`
- Templates de la app: `templates/roster/`
- Carpeta global de archivos estáticos: `static/`
- Carpeta de documentación: `docs/`

## 6. Convenciones de código

- Idioma del código: inglés
- Idioma de la UI: español
- Nombre de apps: inglés, minúsculas
- Nombres de vistas FBV: `snake_case`
- Templates: `snake_case.html`
- URLs: con namespace
- Variables de entorno: `UPPER_SNAKE_CASE`

## 7. Decisiones de entorno

- Base de datos local: SQLite
- Base de datos de producción: por definir más adelante
- Un solo `settings.py` en la v1
- Secretos cargados desde `.env`
- `.env` nunca debe subirse al repositorio
- `.env.example` debe contener solo placeholders

## 8. Decisiones de modelos

- Todos los modelos de dominio usan `created_at` y `updated_at`
- `__str__` es obligatorio
- No se usa soft delete en la v1
- No se usan UUIDs en la v1
- No hay campos monetarios en este proyecto
- Las reglas importantes de integridad deben reforzarse a nivel de base de datos cuando sea razonable

## 9. Modelo de dominio

### Pokemon
Representa la ficha base normalizada de un Pokémon obtenida desde PokeAPI y cacheada localmente.

### RosterEntry
Representa la presencia actual de un Pokémon en la colección del usuario, ya sea en la Party o en la PC Box.

## 10. Manejo de errores

- Si PokeAPI falla, la página no debe romperse.
- La app no debe guardar datos incompletos o parciales.
- El usuario debe recibir un mensaje amigable.
- El dashboard debe seguir siendo usable.

## 11. Ordenamientos y navegación

- Party y PC Box pueden ordenarse por separado.
- Los criterios disponibles son:
  - inicial
  - hp
  - attack
  - defense
  - speed
  - total_power
- Al usar acciones de ordenamiento o liberación, la interfaz debe volver a la sección correspondiente mediante anchors (`#party-section`, `#box-section`, `#capture-section`).

## 12. Decisiones de UI

- Dirección visual: mezcla de estética Pokémon, Y2K/retro-tech de inicios de los 2000 y glassmorphism moderado.
- Intensidad visual: equilibrada.
- Selector de tipos: grid visual, no dropdown.
- Responsive desde la base.
- `Total Power` debe tener un peso visual claro dentro de cada card.
- Las acciones destructivas deben verse secundarias respecto a la información principal.

## 13. Testing mínimo

Como mínimo, se debe testear:
- `__str__` y propiedades importantes del modelo
- lógica principal de captura
- prevención de duplicados
- flujo Party / Box
- liberación desde Party y Box
- autopromoción desde Box a Party
- ordenamiento por `total_power`
- flujo de optimización
- respuesta pública del dashboard
- redirects principales con anchors

## 14. Expectativas de entrega

El proyecto final debe incluir:
- README claro
- instrucciones de instalación
- instrucciones de ejecución
- explicación de decisiones técnicas
- tests ejecutables
- repositorio público en GitHub