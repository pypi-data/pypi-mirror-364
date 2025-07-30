# LocalDex

A fast, offline-first Python library for Pokemon data access. LocalDex provides comprehensive Pokemon information without requiring network requests.

[![PyPI version](https://badge.fury.io/py/localdex.svg)](https://badge.fury.io/py/localdex)
[![Python versions](https://img.shields.io/pypi/pyversions/localdex.svg)](https://pypi.org/project/localdex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Offline Access**: All data stored locally - no network requests required
- **Fast Lookups**: Optimized caching and search capabilities
- **Comprehensive Data**: Pokemon, moves, abilities, and items
- **CLI Interface**: Command-line access to all data
- **Type Hints**: Full type support for better development experience
- **Stat Calculations**: Built-in stat calculation methods

## Installation

```bash
pip install localdex
```

## Quick Start

```python
from localdex import LocalDex

# Initialize the dex
dex = LocalDex()

# Get Pokemon by name or ID
pikachu = dex.get_pokemon("pikachu")
charizard = dex.get_pokemon_by_id(6)

# Get moves and abilities
thunderbolt = dex.get_move("thunderbolt")
lightning_rod = dex.get_ability("lightning-rod")

# Search Pokemon
fire_types = dex.search_pokemon(type="fire")
fast_pokemon = dex.search_pokemon(min_speed=120)
legendary_fire = dex.search_pokemon(type="fire", is_legendary=True)

# Get all data
all_pokemon = dex.get_all_pokemon()
all_moves = dex.get_all_moves()
```

## CLI Usage

```bash
# Get Pokemon information
localdex pokemon pikachu
localdex pokemon 25

# Search Pokemon
localdex search --type Fire --generation 1
localdex search --legendary --min-attack 100

# Get move and ability info
localdex move thunderbolt
localdex ability lightningrod

# List data
localdex list-pokemon --generation 1
localdex list-moves --type Electric

# Export data
localdex export --format json --output pokemon_data.json

# Run demo
localdex demo
```

## API Reference

### Core Methods

- `get_pokemon(name_or_id)` - Get Pokemon by name or ID
- `get_pokemon_by_id(id)` - Get Pokemon by ID
- `get_pokemon_by_name(name)` - Get Pokemon by name
- `get_move(name)` - Get move by name
- `get_ability(name)` - Get ability by name
- `get_item(name)` - Get item by name
- `search_pokemon(**filters)` - Search Pokemon with filters
- `get_all_pokemon()` - Get all Pokemon
- `get_all_moves()` - Get all moves
- `get_all_abilities()` - Get all abilities
- `get_all_items()` - Get all items

### Search Filters

```python
# Available filters for search_pokemon()
dex.search_pokemon(
    type="Fire",              # Pokemon type
    generation=1,             # Generation number
    is_legendary=True,        # Legendary Pokemon
    is_mythical=True,         # Mythical Pokemon
    min_attack=100,           # Minimum attack stat
    max_speed=50,             # Maximum speed stat
    name_contains="char"      # Name contains text
)
```

### Data Models

```python
# Pokemon model
pokemon = dex.get_pokemon("pikachu")
print(f"{pokemon.name} - {pokemon.types}")
print(f"HP: {pokemon.base_stats.hp}")
print(f"Attack: {pokemon.base_stats.attack}")

# Move model
move = dex.get_move("thunderbolt")
print(f"{move.name} - Power: {move.base_power}, Type: {move.type}")

# Ability model
ability = dex.get_ability("lightning-rod")
print(f"{ability.name} - {ability.description}")
```

## Stat Calculations

LocalDex includes methods for calculating Pokemon stats:

```python
# Calculate stats with IVs, EVs, and level
hp = dex.get_hp_stat_from_species("pikachu", iv=31, ev=252, level=100)
attack = dex.get_attack_stat_from_species("pikachu", iv=31, ev=252, level=100)

# Generic stat calculation
hp = dex.calculate_hp(base=35, iv=31, ev=252, level=100)
attack = dex.calculate_other_stat(base=55, iv=31, ev=252, level=100, nature_modifier=1.1)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Data Sources

Data sourced from [Pokemon Showdown](https://github.com/smogon/pokemon-showdown) and [PokeAPI](https://pokeapi.co/).


