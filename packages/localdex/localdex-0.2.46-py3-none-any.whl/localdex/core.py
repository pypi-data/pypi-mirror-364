"""
Core LocalDex functionality.

This module contains the main LocalDex class that provides access to
Pokemon data with caching, search capabilities, and data loading.
"""

import json
import math
import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from functools import lru_cache

from .models import Pokemon, Move, Ability, Item, BaseStats
from .exceptions import (
    PokemonNotFoundError, MoveNotFoundError, AbilityNotFoundError, 
    ItemNotFoundError, DataLoadError, SearchError
)
from .data_loader import DataLoader
from .name_normalizer import PokemonNameNormalizer


class LocalDex:
    """
    Main class for accessing Pokemon data.
    
    This class provides fast, offline access to Pokemon data including
    Pokemon, moves, abilities, and items. It includes caching for
    performance and comprehensive search capabilities.
    """
    
    def __init__(self, data_path: Optional[str] = None, data_dir: Optional[str] = None, enable_caching: bool = True):
        """
        Initialize the LocalDex.
        
        Args:
            data_path: Optional path to data directory. If None, uses package data.
            data_dir: Alias for data_path for backward compatibility.
            enable_caching: Whether to enable caching for better performance.
        """
        # Use data_dir if provided, otherwise use data_path
        final_data_path = data_dir if data_dir is not None else data_path
        self.data_loader = DataLoader(final_data_path)
        self.data_dir = final_data_path  # Store for backward compatibility
        self.enable_caching = enable_caching
        
        # Initialize caches
        self._pokemon_cache: Dict[str, Pokemon] = {}
        self._pokemon_id_cache: Dict[int, Pokemon] = {}
        self._move_cache: Dict[str, Move] = {}
        self._ability_cache: Dict[str, Ability] = {}
        self._item_cache: Dict[str, Item] = {}
        
        # Search indexes
        self._pokemon_by_type: Dict[str, Set[str]] = {}
        self._pokemon_by_generation: Dict[int, Set[str]] = {}
        self._moves_by_type: Dict[str, Set[str]] = {}
        self._moves_by_category: Dict[str, Set[str]] = {}
        
        # Load data if caching is enabled
        if self.enable_caching:
            self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build search indexes for faster lookups."""
        try:
            # Build Pokemon indexes
            all_pokemon = self.get_all_pokemon()
            
            for pokemon in all_pokemon:
                # Index by type
                for pokemon_type in pokemon.types:
                    if pokemon_type not in self._pokemon_by_type:
                        self._pokemon_by_type[pokemon_type] = set()
                    self._pokemon_by_type[pokemon_type].add(pokemon.name.lower())
                
                # Index by generation
                if pokemon.generation:
                    if pokemon.generation not in self._pokemon_by_generation:
                        self._pokemon_by_generation[pokemon.generation] = set()
                    self._pokemon_by_generation[pokemon.generation].add(pokemon.name.lower())
            
            # Build move indexes
            all_moves = self.get_all_moves()
            
            for move in all_moves:
                # Index by type
                if move.type not in self._moves_by_type:
                    self._moves_by_type[move.type] = set()
                self._moves_by_type[move.type].add(move.name.lower())
                
                # Index by category
                if move.category not in self._moves_by_category:
                    self._moves_by_category[move.category] = set()
                self._moves_by_category[move.category].add(move.name.lower())
                
        except Exception as e:
            # If indexing fails, continue without indexes
            pass
    
    def get_pokemon(self, name_or_id: Union[str, int]) -> Pokemon:
        """
        Get a Pokemon by name or ID.
        
        Args:
            name_or_id: Pokemon name (case-insensitive) or ID number
            
        Returns:
            Pokemon object
            
        Raises:
            PokemonNotFoundError: If Pokemon is not found
        """
        if isinstance(name_or_id, int):
            return self.get_pokemon_by_id(name_or_id)
        else:
            return self.get_pokemon_by_name(name_or_id)
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Pokemon:
        """
        Get a Pokemon by ID.
        
        Args:
            pokemon_id: Pokemon ID number
            
        Returns:
            Pokemon object
            
        Raises:
            PokemonNotFoundError: If Pokemon is not found
        """
        # Check cache first
        if self.enable_caching and pokemon_id in self._pokemon_id_cache:
            return self._pokemon_id_cache[pokemon_id]
        
        # Load from data
        pokemon_data = self.data_loader.load_pokemon_by_id(pokemon_id)
        if not pokemon_data:
            raise PokemonNotFoundError(str(pokemon_id))
        
        pokemon = self._create_pokemon_from_data(pokemon_data)
        
        # Cache the result
        if self.enable_caching:
            self._pokemon_id_cache[pokemon_id] = pokemon
            self._pokemon_cache[pokemon.name.lower()] = pokemon
        
        return pokemon
    
    def get_pokemon_by_name(self, name: str) -> Pokemon:
        """
        Get a Pokemon by name.
        
        Args:
            name: Pokemon name (case-insensitive)
            
        Returns:
            Pokemon object
            
        Raises:
            PokemonNotFoundError: If Pokemon is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._pokemon_cache:
            return self._pokemon_cache[name_lower]
        
        # Load from data
        pokemon_data = self.data_loader.load_pokemon_by_name(name)
        if not pokemon_data:
            # Try with normalized name
            normalized_name = PokemonNameNormalizer.normalize_name(name)
            pokemon_data = self.data_loader.load_pokemon_by_name(normalized_name)
            
            if not pokemon_data:
                raise PokemonNotFoundError(name)
        
        
        pokemon = self._create_pokemon_from_data(pokemon_data)
        
        # Cache the result
        if self.enable_caching:
            self._pokemon_cache[name_lower] = pokemon
            self._pokemon_id_cache[pokemon.id] = pokemon
        
        return pokemon
    
    def get_move(self, name: str) -> Move:
        """
        Get a move by name.
        
        Args:
            name: Move name (case-insensitive)
            
        Returns:
            Move object
            
        Raises:
            MoveNotFoundError: If move is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._move_cache:
            return self._move_cache[name_lower]
        
        # Load from data
        move_data = self.data_loader.load_move(name)
        if not move_data:
            raise MoveNotFoundError(name)
        
        move = self._create_move_from_data(move_data)
        
        # Cache the result
        if self.enable_caching:
            self._move_cache[name_lower] = move
        
        return move
    
    def get_ability(self, name: str) -> Ability:
        """
        Get an ability by name.
        
        Args:
            name: Ability name (case-insensitive)
            
        Returns:
            Ability object
            
        Raises:
            AbilityNotFoundError: If ability is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._ability_cache:
            return self._ability_cache[name_lower]
        
        # Load from data
        ability_data = self.data_loader.load_ability(name)
        if not ability_data:
            raise AbilityNotFoundError(name)
        
        ability = self._create_ability_from_data(ability_data)
        
        # Cache the result
        if self.enable_caching:
            self._ability_cache[name_lower] = ability
        
        return ability
    
    def get_item(self, name: str) -> Item:
        """
        Get an item by name.
        
        Args:
            name: Item name (case-insensitive)
            
        Returns:
            Item object
            
        Raises:
            ItemNotFoundError: If item is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._item_cache:
            return self._item_cache[name_lower]
        
        # Load from data
        item_data = self.data_loader.load_item(name)
        if not item_data:
            raise ItemNotFoundError(name)
        
        item = self._create_item_from_data(item_data)
        
        # Cache the result
        if self.enable_caching:
            self._item_cache[name_lower] = item
        
        return item
    
    def search_pokemon(self, **filters) -> List[Pokemon]:
        """
        Search for Pokemon using various filters.
        
        Args:
            **filters: Search filters including:
                - type: Pokemon type (e.g., "Fire", "Water")
                - generation: Generation number (1-9)
                - min_attack: Minimum attack stat
                - max_attack: Maximum attack stat
                - min_special_attack: Minimum special attack stat
                - max_special_attack: Maximum special attack stat
                - min_speed: Minimum speed stat
                - max_speed: Maximum speed stat
                - min_hp: Minimum HP stat
                - max_hp: Maximum HP stat
                - is_legendary: Whether Pokemon is legendary
                - is_mythical: Whether Pokemon is mythical
                - name_contains: Partial name match
                
        Returns:
            List of Pokemon matching the filters
        """
        try:
            # Use indexes for faster search if available
            if self.enable_caching and self._pokemon_by_type and self._pokemon_by_generation:
                return self._search_pokemon_with_indexes(**filters)
            else:
                return self._search_pokemon_full_scan(**filters)
        except Exception as e:
            raise SearchError(f"Error during Pokemon search: {e}")
    
    def _search_pokemon_with_indexes(self, **filters) -> List[Pokemon]:
        """Search Pokemon using pre-built indexes."""
        candidate_names = set()
        
        # Filter by type
        if "type" in filters:
            pokemon_type = filters["type"].lower()
            if pokemon_type in self._pokemon_by_type:
                if not candidate_names:
                    candidate_names = self._pokemon_by_type[pokemon_type].copy()
                else:
                    candidate_names &= self._pokemon_by_type[pokemon_type]
        
        # Filter by generation
        if "generation" in filters:
            generation = filters["generation"]
            if generation in self._pokemon_by_generation:
                if not candidate_names:
                    candidate_names = self._pokemon_by_generation[generation].copy()
                else:
                    candidate_names &= self._pokemon_by_generation[generation]
        
        # If no candidates from indexes, do full scan
        if not candidate_names:
            return self._search_pokemon_full_scan(**filters)
        
        # Load and filter candidates
        results = []
        for name in candidate_names:
            try:
                pokemon = self.get_pokemon_by_name(name)
                if self._pokemon_matches_filters(pokemon, filters):
                    results.append(pokemon)
            except PokemonNotFoundError:
                continue
        
        return results
    
    def _search_pokemon_full_scan(self, **filters) -> List[Pokemon]:
        """Search Pokemon by scanning all data."""
        results = []
        all_pokemon = self.get_all_pokemon()
        
        for pokemon in all_pokemon:
            if self._pokemon_matches_filters(pokemon, filters):
                results.append(pokemon)
        
        return results
    
    def _pokemon_matches_filters(self, pokemon: Pokemon, filters: Dict[str, Any]) -> bool:
        """Check if a Pokemon matches the given filters."""
        # Type filter
        if "type" in filters:
            if filters["type"].lower() not in [t.lower() for t in pokemon.types]:
                return False
        
        # Generation filter
        if "generation" in filters:
            if pokemon.generation != filters["generation"]:
                return False
        
        # Stat filters
        if "min_attack" in filters and pokemon.base_stats.attack < filters["min_attack"]:
            return False
        if "max_attack" in filters and pokemon.base_stats.attack > filters["max_attack"]:
            return False
        if "min_special_attack" in filters and pokemon.base_stats.special_attack < filters["min_special_attack"]:
            return False
        if "max_special_attack" in filters and pokemon.base_stats.special_attack > filters["max_special_attack"]:
            return False
        if "min_speed" in filters and pokemon.base_stats.speed < filters["min_speed"]:
            return False
        if "max_speed" in filters and pokemon.base_stats.speed > filters["max_speed"]:
            return False
        if "min_hp" in filters and pokemon.base_stats.hp < filters["min_hp"]:
            return False
        if "max_hp" in filters and pokemon.base_stats.hp > filters["max_hp"]:
            return False
        
        # Legendary/Mythical filters
        if "is_legendary" in filters and pokemon.is_legendary != filters["is_legendary"]:
            return False
        if "is_mythical" in filters and pokemon.is_mythical != filters["is_mythical"]:
            return False
        
        # Name contains filter
        if "name_contains" in filters:
            if filters["name_contains"].lower() not in pokemon.name.lower():
                return False
        
        return True
    
    def get_all_pokemon(self) -> List[Pokemon]:
        """Get all Pokemon."""
        pokemon_data_list = self.data_loader.load_all_pokemon()
        return [self._create_pokemon_from_data(data) for data in pokemon_data_list]
    
    def get_all_moves(self) -> List[Move]:
        """Get all moves."""
        move_data_list = self.data_loader.load_all_moves()
        return [self._create_move_from_data(data) for data in move_data_list]
    
    def get_all_abilities(self) -> List[Ability]:
        """Get all abilities."""
        ability_data_list = self.data_loader.load_all_abilities()
        return [self._create_ability_from_data(data) for data in ability_data_list]
    
    def get_all_items(self) -> List[Item]:
        """Get all items."""
        item_data_list = self.data_loader.load_all_items()
        return [self._create_item_from_data(data) for data in item_data_list]
    
    def _create_pokemon_from_data(self, data: Dict[str, Any]) -> Pokemon:
        """Create a Pokemon object from raw data."""
        # Create base stats
        base_stats_data = data.get("baseStats", {})
        base_stats = BaseStats(
            hp=base_stats_data.get("hp", 0),
            attack=base_stats_data.get("attack", 0),
            defense=base_stats_data.get("defense", 0),
            special_attack=base_stats_data.get("special_attack", 0),
            special_defense=base_stats_data.get("special_defense", 0),
            speed=base_stats_data.get("speed", 0),
        )
        return Pokemon(
            id=data["id"],
            name=data["name"],
            types=data.get("types", []),
            base_stats=base_stats,
            height=data.get("height"),
            weight=data.get("weight"),
            color=data.get("color"),
            abilities=data.get("abilities", {}),
            moves=data.get("moves", []),
            learnset=data.get("learnset", {}),
            evolutions=data.get("evolutions", []),
            prevo=data.get("prevo"),
            evo_level=data.get("evoLevel"),
            evo_type=data.get("evoType"),
            evo_condition=data.get("evoCondition"),
            evo_item=data.get("evoItem"),
            egg_groups=data.get("eggGroups", []),
            gender_ratio=data.get("genderRatio", {}),
            generation=data.get("generation"),
            description=data.get("description"),
            is_legendary=data.get("isLegendary", False),
            is_mythical=data.get("isMythical", False),
            is_ultra_beast=data.get("isUltraBeast", False),
            metadata=data.get("metadata", {}),
        )
    
    def _create_move_from_data(self, data: Dict[str, Any]) -> Move:
        """Create a Move object from raw data."""
        return Move(
            name=data.get("name", ""),
            type=data.get("type", "Normal"),
            category=data.get("category", "Status"),
            base_power=data.get("basePower", 0),
            accuracy=data.get("accuracy", 100),
            pp=data.get("pp", 10),
            priority=data.get("priority", 0),
            target=data.get("target", "normal"),
            description=data.get("desc"),
            short_description=data.get("shortDesc"),
            contest_type=data.get("contestType"),
            crit_ratio=data.get("critRatio", 1),
            secondary_effects=data.get("secondary"),
            flags=data.get("flags", {}),
            drain=data.get("drain"),
            z_move=data.get("isZ"),
            z_move_type=data.get("zMoveType"),
            z_move_from=data.get("zMoveFrom"),
            generation=data.get("num"),
            is_nonstandard=data.get("isNonstandard"),
            metadata=data
        )
    
    def _create_ability_from_data(self, data: Dict[str, Any]) -> Ability:
        """Create an Ability object from raw data."""
        return Ability(
            name=data.get("name", ""),
            description=data.get("description", data.get("desc", "")),
            short_description=data.get("short_description", data.get("shortDesc", "")),
            generation=data.get("generation", data.get("gen")),
            rating=data.get("rating"),
            num=data.get("num"),
            effect=data.get("effect"),
            effect_entries=data.get("effect_entries"),
            metadata=data
        )
    
    def _create_item_from_data(self, data: Dict[str, Any]) -> Item:
        """Create an Item object from raw data."""
        return Item(
            name=data.get("name", ""),
            description=data.get("description", data.get("desc", "")),
            short_description=data.get("shortDesc"),
            generation=data.get("gen"),
            num=data.get("num"),
            spritenum=data.get("spritenum"),
            fling=data.get("fling"),
            mega_stone=data.get("megaStone"),
            mega_evolves=data.get("megaEvolves"),
            z_move=data.get("zMove"),
            z_move_type=data.get("zMoveType"),
            z_move_from=data.get("zMoveFrom"),
            item_user=data.get("itemUser"),
            on_plate=data.get("onPlate"),
            on_drive=data.get("onDrive"),
            on_memory=data.get("onMemory"),
            forced_forme=data.get("forcedForme"),
            is_nonstandard=data.get("isNonstandard"),
            category=data.get("category"),
            metadata=data
        )
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._pokemon_cache.clear()
        self._pokemon_id_cache.clear()
        self._move_cache.clear()
        self._ability_cache.clear()
        self._item_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "pokemon_by_name": len(self._pokemon_cache),
            "pokemon_by_id": len(self._pokemon_id_cache),
            "moves": len(self._move_cache),
            "abilities": len(self._ability_cache),
            "items": len(self._item_cache)
        }
    def get_base_stats_from_species(self, species: str):
        """Get base stats from species name"""
        return self.get_pokemon(name_or_id=species).base_stats
    
    def get_hp_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100) -> int:
        """Calculate HP stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_hp(base_stats.hp, iv, ev, level)

    def get_attack_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Attack stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.attack, iv, ev, level, nature_modifier)
    
    def get_defense_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Defense stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.defense, iv, ev, level, nature_modifier)
    
    def get_special_attack_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Special Attack stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.special_attack, iv, ev, level, nature_modifier)
    
    def get_special_defense_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Special Defense stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.special_defense, iv, ev, level, nature_modifier)
    
    def get_speed_stat_from_species(self, species: str, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """Calculate Speed stat for a species with given IVs, EVs, and level"""
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_other_stat(base_stats.speed, iv, ev, level, nature_modifier)
    
    def get_substitute_health_from_species(self, species: str, iv: int, ev: int, level: int = 100) -> int:
        """Calculate substitute health for a species (1/4 of max HP)"""
        max_hp = self.get_hp_stat_from_species(species, iv, ev, level)
        return int(max_hp / 4)
    
    def calculate_hp(self, base: int, iv: int, ev: int, level: int = 100) -> int:
        """
        Calculate HP using the Pokemon HP formula.
        
        Args:
            base (int): Base HP stat
            iv (int): Individual Value (0-31)
            ev (int): Effort Value (0-252)
            level (int): Pokemon level (1-100)
        
        Returns:
            int: Calculated HP value
        """
        hp = math.floor(((2 * base + iv + math.floor(ev / 4)) * level) / 100) + level + 10
        return hp
        
    def calculate_other_stat(self, base: int, iv: int, ev: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate other stats (Attack, Defense, Sp. Attack, Sp. Defense, Speed) using the Pokemon stat formula.
        
        Args:
            base (int): Base stat value
            iv (int): Individual Value (0-31)
            ev (int): Effort Value (0-252)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Calculated stat value
        """
        stat = math.floor((math.floor(((2 * base + iv + math.floor(ev / 4)) * level) / 100) + 5) * nature_modifier)
        return stat

    def calculate_hp_ev(self, total_hp: int, base_hp: int, iv: int, level: int = 100) -> int:
        """
        Calculate HP EV from total HP stat using the reverse of the Pokemon HP formula.
        
        If the target HP is impossible to achieve with any EV value, returns the EV that
        produces the closest possible HP value. For impossibly high HP values, returns 252 EVs.
        For impossibly low HP values, returns 0 EVs.
        
        Args:
            total_hp (int): Total HP stat value
            base_hp (int): Base HP stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        if level <= 0:
            raise ValueError("Level must be greater than 0")
        
        # Calculate the minimum and maximum possible HP values
        min_hp = self.calculate_hp(base_hp, iv, 0, level)
        max_hp = self.calculate_hp(base_hp, iv, 252, level)
        
        # If target HP is impossible, return the closest boundary
        if total_hp <= min_hp:
            return 0  # Return 0 EVs for impossibly low HP
        elif total_hp >= max_hp:
            return 252  # Return 252 EVs for impossibly high HP
        
        # Find the EV that gives us the closest HP value
        best_ev = 0
        best_diff = float('inf')
        
        for test_ev in range(0, 253, 4):  # EVs are always multiples of 4
            test_hp = self.calculate_hp(base_hp, iv, test_ev, level)
            diff = abs(test_hp - total_hp)
            
            if diff < best_diff:
                best_diff = diff
                best_ev = test_ev
            elif diff == best_diff and test_ev < best_ev:
                # If we have the same difference, prefer the lower EV
                best_ev = test_ev
        
        return best_ev
    
    def calculate_other_stat_ev(self, total_stat: int, base_stat: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate EV for other stats (Attack, Defense, Sp. Attack, Sp. Defense, Speed) using the reverse of the Pokemon stat formula.
        
        If the target stat is impossible to achieve with any EV value, returns the EV that
        produces the closest possible stat value. For impossibly high stat values, returns 252 EVs.
        For impossibly low stat values, returns 0 EVs.
        
        Args:
            total_stat (int): Total stat value
            base_stat (int): Base stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        if level <= 0:
            raise ValueError("Level must be greater than 0")
        if nature_modifier <= 0:
            raise ValueError("Nature modifier must be greater than 0")
        
        # Calculate the minimum and maximum possible stat values
        min_stat = self.calculate_other_stat(base_stat, iv, 0, level, nature_modifier)
        max_stat = self.calculate_other_stat(base_stat, iv, 252, level, nature_modifier)
        
        # If target stat is impossible, return the closest boundary
        if total_stat <= min_stat:
            return 0  # Return 0 EVs for impossibly low stat
        elif total_stat >= max_stat:
            return 252  # Return 252 EVs for impossibly high stat
        
        # Find the EV that gives us the closest stat value
        best_ev = 0
        best_diff = float('inf')
        
        for test_ev in range(0, 253, 4):  # EVs are always multiples of 4
            test_stat = self.calculate_other_stat(base_stat, iv, test_ev, level, nature_modifier)
            diff = abs(test_stat - total_stat)
            
            if diff < best_diff:
                best_diff = diff
                best_ev = test_ev
            elif diff == best_diff and test_ev < best_ev:
                # If we have the same difference, prefer the lower EV
                best_ev = test_ev
        
        return best_ev
    
    def calculate_attack_ev(self, total_attack: int, base_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Attack EV from total Attack stat.
        
        If the target Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Attack value. For impossibly high Attack values, returns 252 EVs.
        For impossibly low Attack values, returns 0 EVs.
        
        Args:
            total_attack (int): Total Attack stat value
            base_attack (int): Base Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_attack, base_attack, iv, level, nature_modifier)
    
    def calculate_defense_ev(self, total_defense: int, base_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Defense EV from total Defense stat.
        
        If the target Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Defense value. For impossibly high Defense values, returns 252 EVs.
        For impossibly low Defense values, returns 0 EVs.
        
        Args:
            total_defense (int): Total Defense stat value
            base_defense (int): Base Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_defense, base_defense, iv, level, nature_modifier)
    
    def calculate_special_attack_ev(self, total_special_attack: int, base_special_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Attack EV from total Special Attack stat.
        
        If the target Special Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Attack value. For impossibly high Special Attack values, returns 252 EVs.
        For impossibly low Special Attack values, returns 0 EVs.
        
        Args:
            total_special_attack (int): Total Special Attack stat value
            base_special_attack (int): Base Special Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_special_attack, base_special_attack, iv, level, nature_modifier)
    
    def calculate_special_defense_ev(self, total_special_defense: int, base_special_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Defense EV from total Special Defense stat.
        
        If the target Special Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Defense value. For impossibly high Special Defense values, returns 252 EVs.
        For impossibly low Special Defense values, returns 0 EVs.
        
        Args:
            total_special_defense (int): Total Special Defense stat value
            base_special_defense (int): Base Special Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_special_defense, base_special_defense, iv, level, nature_modifier)
    
    def calculate_speed_ev(self, total_speed: int, base_speed: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Speed EV from total Speed stat.
        
        If the target Speed is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Speed value. For impossibly high Speed values, returns 252 EVs.
        For impossibly low Speed values, returns 0 EVs.
        
        Args:
            total_speed (int): Total Speed stat value
            base_speed (int): Base Speed stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        return self.calculate_other_stat_ev(total_speed, base_speed, iv, level, nature_modifier)

    def calculate_hp_ev_from_species(self, species: str, total_hp: int, iv: int, level: int = 100) -> int:
        """
        Calculate HP EV from total HP stat using species name.
        
        If the target HP is impossible to achieve with any EV value, returns the EV that
        produces the closest possible HP value. For impossibly high HP values, returns 252 EVs.
        For impossibly low HP values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_hp (int): Total HP stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_hp_ev(total_hp, base_stats.hp, iv, level)
    
    def calculate_attack_ev_from_species(self, species: str, total_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Attack EV from total Attack stat using species name.
        
        If the target Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Attack value. For impossibly high Attack values, returns 252 EVs.
        For impossibly low Attack values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_attack (int): Total Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_attack_ev(total_attack, base_stats.attack, iv, level, nature_modifier)
    
    def calculate_defense_ev_from_species(self, species: str, total_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Defense EV from total Defense stat using species name.
        
        If the target Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Defense value. For impossibly high Defense values, returns 252 EVs.
        For impossibly low Defense values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_defense (int): Total Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_defense_ev(total_defense, base_stats.defense, iv, level, nature_modifier)
    
    def calculate_special_attack_ev_from_species(self, species: str, total_special_attack: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Attack EV from total Special Attack stat using species name.
        
        If the target Special Attack is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Attack value. For impossibly high Special Attack values, returns 252 EVs.
        For impossibly low Special Attack values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_special_attack (int): Total Special Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_attack_ev(total_special_attack, base_stats.special_attack, iv, level, nature_modifier)
    
    def calculate_special_defense_ev_from_species(self, species: str, total_special_defense: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Special Defense EV from total Special Defense stat using species name.
        
        If the target Special Defense is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Special Defense value. For impossibly high Special Defense values, returns 252 EVs.
        For impossibly low Special Defense values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_special_defense (int): Total Special Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_defense_ev(total_special_defense, base_stats.special_defense, iv, level, nature_modifier)
    
    def calculate_speed_ev_from_species(self, species: str, total_speed: int, iv: int, level: int = 100, nature_modifier: float = 1.0) -> int:
        """
        Calculate Speed EV from total Speed stat using species name.
        
        If the target Speed is impossible to achieve with any EV value, returns the EV that
        produces the closest possible Speed value. For impossibly high Speed values, returns 252 EVs.
        For impossibly low Speed values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            total_speed (int): Total Speed stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            int: Required EV value (0-252) - closest possible value if target is impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_speed_ev(total_speed, base_stats.speed, iv, level, nature_modifier)
    
    def calculate_all_evs_from_species(self, species: str, stats: Dict[str, int], ivs: Dict[str, int], level: int = 100, nature_modifier: float = 1.0) -> Dict[str, int]:
        """
        Calculate all EV values for a Pokemon using species name and target stats.
        
        If any target stat is impossible to achieve with any EV value, returns the EV that
        produces the closest possible stat value. For impossibly high stat values, returns 252 EVs.
        For impossibly low stat values, returns 0 EVs.
        
        Args:
            species (str): Pokemon species name
            stats (Dict[str, int]): Dictionary of target stat values with keys: 'hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed'
            ivs (Dict[str, int]): Dictionary of IV values with keys: 'hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed'
            level (int): Pokemon level (1-100)
            nature_modifier (float): Nature modifier (0.9 for hindering, 1.0 for neutral, 1.1 for beneficial)
        
        Returns:
            Dict[str, int]: Dictionary of required EV values for each stat - closest possible values if targets are impossible
        """
        base_stats = self.get_base_stats_from_species(species)
        
        evs = {}
        
        # Calculate HP EV (no nature modifier)
        if 'hp' in stats:
            evs['hp'] = self.calculate_hp_ev(stats['hp'], base_stats.hp, ivs.get('hp', 31), level)
        
        # Calculate other stat EVs (with nature modifier)
        if 'attack' in stats:
            evs['attack'] = self.calculate_attack_ev(stats['attack'], base_stats.attack, ivs.get('attack', 31), level, nature_modifier)
        
        if 'defense' in stats:
            evs['defense'] = self.calculate_defense_ev(stats['defense'], base_stats.defense, ivs.get('defense', 31), level, nature_modifier)
        
        if 'special_attack' in stats:
            evs['special_attack'] = self.calculate_special_attack_ev(stats['special_attack'], base_stats.special_attack, ivs.get('special_attack', 31), level, nature_modifier)
        
        if 'special_defense' in stats:
            evs['special_defense'] = self.calculate_special_defense_ev(stats['special_defense'], base_stats.special_defense, ivs.get('special_defense', 31), level, nature_modifier)
        
        if 'speed' in stats:
            evs['speed'] = self.calculate_speed_ev(stats['speed'], base_stats.speed, ivs.get('speed', 31), level, nature_modifier)
        
        return evs

    def calculate_hp_ev_and_nature_combinations(self, total_hp: int, base_hp: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible EV and nature modifier combinations for HP.
        Note: HP is not affected by nature, so this returns only the EV value with nature_modifier=1.0.
        
        Args:
            total_hp (int): Total HP stat value
            base_hp (int): Base HP stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        # HP is not affected by nature, so there's only one combination
        ev = self.calculate_hp_ev(total_hp, base_hp, iv, level)
        return [(ev, 1.0)]
    
    def calculate_other_stat_ev_and_nature_combinations(self, total_stat: int, base_stat: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible EV and nature modifier combinations for other stats.
        
        Args:
            total_stat (int): Total stat value
            base_stat (int): Base stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        if level <= 0:
            raise ValueError("Level must be greater than 0")
        
        combinations = []
        
        # Try each nature modifier: hindering (0.9), neutral (1.0), beneficial (1.1)
        nature_modifiers = [0.9, 1.0, 1.1]
        
        for nature_modifier in nature_modifiers:
            try:
                ev = self.calculate_other_stat_ev(total_stat, base_stat, iv, level, nature_modifier)
                
                # Verify this combination actually produces the target stat (or closest possible)
                calculated_stat = self.calculate_other_stat(base_stat, iv, ev, level, nature_modifier)
                
                # Accept the combination if it produces the target stat or the closest possible value
                if calculated_stat == total_stat or abs(calculated_stat - total_stat) <= 1:
                    combinations.append((ev, nature_modifier))
                    
            except (ValueError, ZeroDivisionError):
                # Skip invalid combinations
                continue
        
        # Remove duplicates and sort by EV (ascending)
        unique_combinations = list(set(combinations))
        unique_combinations.sort(key=lambda x: x[0])
        
        return unique_combinations
    
    def calculate_attack_ev_and_nature_combinations(self, total_attack: int, base_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Attack EV and nature modifier combinations.
        
        Args:
            total_attack (int): Total Attack stat value
            base_attack (int): Base Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_attack, base_attack, iv, level)
    
    def calculate_defense_ev_and_nature_combinations(self, total_defense: int, base_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Defense EV and nature modifier combinations.
        
        Args:
            total_defense (int): Total Defense stat value
            base_defense (int): Base Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_defense, base_defense, iv, level)
    
    def calculate_special_attack_ev_and_nature_combinations(self, total_special_attack: int, base_special_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Attack EV and nature modifier combinations.
        
        Args:
            total_special_attack (int): Total Special Attack stat value
            base_special_attack (int): Base Special Attack stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_special_attack, base_special_attack, iv, level)
    
    def calculate_special_defense_ev_and_nature_combinations(self, total_special_defense: int, base_special_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Defense EV and nature modifier combinations.
        
        Args:
            total_special_defense (int): Total Special Defense stat value
            base_special_defense (int): Base Special Defense stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_special_defense, base_special_defense, iv, level)
    
    def calculate_speed_ev_and_nature_combinations(self, total_speed: int, base_speed: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Speed EV and nature modifier combinations.
        
        Args:
            total_speed (int): Total Speed stat value
            base_speed (int): Base Speed stat
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        return self.calculate_other_stat_ev_and_nature_combinations(total_speed, base_speed, iv, level)
    
    def calculate_hp_ev_and_nature_combinations_from_species(self, species: str, total_hp: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible HP EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_hp (int): Total HP stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_hp_ev_and_nature_combinations(total_hp, base_stats.hp, iv, level)
    
    def calculate_attack_ev_and_nature_combinations_from_species(self, species: str, total_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Attack EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_attack (int): Total Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_attack_ev_and_nature_combinations(total_attack, base_stats.attack, iv, level)
    
    def calculate_defense_ev_and_nature_combinations_from_species(self, species: str, total_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Defense EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_defense (int): Total Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_defense_ev_and_nature_combinations(total_defense, base_stats.defense, iv, level)
    
    def calculate_special_attack_ev_and_nature_combinations_from_species(self, species: str, total_special_attack: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Attack EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_special_attack (int): Total Special Attack stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_attack_ev_and_nature_combinations(total_special_attack, base_stats.special_attack, iv, level)
    
    def calculate_special_defense_ev_and_nature_combinations_from_species(self, species: str, total_special_defense: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Special Defense EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_special_defense (int): Total Special Defense stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_special_defense_ev_and_nature_combinations(total_special_defense, base_stats.special_defense, iv, level)
    
    def calculate_speed_ev_and_nature_combinations_from_species(self, species: str, total_speed: int, iv: int, level: int = 100) -> List[Tuple[int, float]]:
        """
        Calculate all possible Speed EV and nature modifier combinations using species name.
        
        Args:
            species (str): Pokemon species name
            total_speed (int): Total Speed stat value
            iv (int): Individual Value (0-31)
            level (int): Pokemon level (1-100)
        
        Returns:
            List[Tuple[int, float]]: List of (EV, nature_modifier) combinations
        """
        base_stats = self.get_base_stats_from_species(species)
        return self.calculate_speed_ev_and_nature_combinations(total_speed, base_stats.speed, iv, level)
