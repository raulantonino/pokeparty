# Pokeparty - Project Decisions

## 1. Project context

- Project type: greenfield technical challenge with external API integration.
- Main deliverable: code + technical documentation.
- Main objective: build a portfolio-quality Django project with strong backend decisions, clean architecture, and polished UI.
- Source of truth: challenge brief + project decisions + real project code.

## 2. Product definition

- The application allows the user to build and optimize a Pokémon party using real data from PokeAPI.
- The project uses server-side rendered HTML with Django templates.
- There is no separate frontend and no mobile app in v1.
- There is no authentication system in v1.
- There are no file uploads in v1.

## 3. Core business rules

- The user captures one random Pokémon based on a selected type.
- A Pokémon cannot be duplicated in the current collection.
- The Party can contain a maximum of 6 Pokémon.
- Extra Pokémon go to the PC Box automatically.
- A Pokémon can only be released from the PC Box.
- Releasing a Pokémon removes the local roster entry only.
- Pokémon data must persist in the local database.
- The "best team possible" flow uses all 6 base stats:
  - hp
  - attack
  - defense
  - special_attack
  - special_defense
  - speed
- Tie-breaks in optimization:
  1. higher total_power
  2. better type diversity in the final Party
  3. stronger best individual stat
  4. higher speed
  5. lower external_id for deterministic ordering

## 4. Architecture decisions

- Architecture style: Django SSR + ORM.
- No DRF in v1.
- External API: PokeAPI.
- PokeAPI integration will live in a dedicated service layer.
- Roster/optimization logic will live in a separate internal service layer.
- Views must stay thin.
- Query logic that repeats should move to queryset/manager or service layer.

## 5. Project structure

- Global config folder: `config/`
- Main app: `roster`
- Global templates folder: `templates/`
- App templates folder: `templates/roster/`
- Global static folder: `static/`
- Docs folder: `docs/`

## 6. Code conventions

- Code language: English
- UI language: Spanish
- App names: English, lowercase
- FBV names: snake_case
- Template names: snake_case.html
- URLs: namespaced
- Environment variables: UPPER_SNAKE_CASE

## 7. Environment decisions

- Local database: SQLite
- Production database: to be defined later
- Single `settings.py` in v1
- Secrets loaded from `.env`
- `.env` must never be committed
- `.env.example` must contain placeholders only

## 8. Model decisions

- All domain models use `created_at` and `updated_at`
- `__str__` is mandatory
- No soft delete in v1
- No UUIDs in v1
- No money fields in this project
- Important integrity rules should be enforced at database level when reasonable

## 9. Domain model plan

### Pokemon
Normalized Pokémon data retrieved from PokeAPI and cached locally.

### RosterEntry
Represents a Pokémon currently present in the user's collection, either in the Party or in the PC Box.

## 10. Error handling decisions

- If PokeAPI fails, the page must not break.
- The app must not save incomplete or partial Pokémon data.
- The user should receive a friendly message.
- The dashboard should remain usable.

## 11. Testing minimum

At minimum, test:
- important model `__str__`
- basic model constraints/logic
- public dashboard response
- main capture flow
- optimization flow

## 12. Delivery expectations

The final project must include:
- clear README
- setup instructions
- run instructions
- explanation of technical decisions
- public GitHub repository