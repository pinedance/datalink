"""
Core DataLink utilities
Shared functions for loading and manipulating DataLink data

This module provides the core functionality for loading YAML-based linked data
and extracting specific entities and relationships for the DataLink project.
"""

import yaml
from pathlib import Path
import glob


def load_datalink():
    """
    Load and parse all YAML files from data/datalink/ directory

    Supports both the new multi-file directory structure (data/datalink/*.yaml)
    and the legacy single file structure (data/datalink.yaml) for backward compatibility.

    Returns:
        dict: Combined data structure with 'entities' and 'relationships' keys
              containing lists of all loaded entities and relationships

    Structure:
        {
            "entities": [
                {
                    "id": "unique_identifier",
                    "name": "Entity Name",
                    "type": "entity_type",
                    "description": "Optional description",
                    "properties": {...},
                    "image_links": [...],
                    "external_links": [...]
                },
                ...
            ],
            "relationships": [
                {
                    "from": "source_entity_id",
                    "to": "target_entity_id",
                    "type": "relationship_type",
                    "properties": {...}
                },
                ...
            ]
        }
    """
    datalink_dir = Path("data/datalink")

    # Initialize combined data structure
    combined_data = {"entities": [], "relationships": []}

    # Check if new directory structure exists
    if datalink_dir.exists() and datalink_dir.is_dir():
        # Load from multiple YAML files in data/datalink/
        # Support both .yaml and .yml extensions
        yaml_files = glob.glob(str(datalink_dir / "*.yaml")) + glob.glob(str(datalink_dir / "*.yml"))

        # Process files in sorted order for consistent results
        for yaml_file in sorted(yaml_files):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as file:
                    file_data = yaml.safe_load(file)
                    if file_data:
                        # Merge entities from this file
                        if 'entities' in file_data:
                            combined_data['entities'].extend(file_data['entities'])
                        # Merge relationships from this file
                        if 'relationships' in file_data:
                            combined_data['relationships'].extend(file_data['relationships'])
            except Exception as e:
                print(f"Warning: Could not load {yaml_file}: {e}")

    # Fallback to legacy single file structure for backward compatibility
    if not combined_data['entities'] and not combined_data['relationships']:
        datalink_path = Path("data/datalink.yaml")
        if datalink_path.exists():
            try:
                with open(datalink_path, 'r', encoding='utf-8') as file:
                    old_data = yaml.safe_load(file)
                    if old_data:
                        combined_data = old_data
            except Exception as e:
                print(f"Warning: Could not load {datalink_path}: {e}")

    return combined_data


def get_entity_by_id(data, entity_id):
    """
    Get a specific entity by its unique identifier

    Args:
        data (dict): Combined DataLink data structure
        entity_id (str): Unique identifier for the entity

    Returns:
        dict or None: Entity data if found, None otherwise
    """
    for entity in data.get("entities", []):
        if entity["id"] == entity_id:
            return entity
    return None


def get_entity_relationships(data, entity_id):
    """
    Get all relationships for a specific entity

    Searches for relationships where the entity is either the source (from)
    or target (to) of the relationship.

    Args:
        data (dict): Combined DataLink data structure
        entity_id (str): Unique identifier for the entity

    Returns:
        list: List of relationship objects involving the specified entity
    """
    relationships = []

    for rel in data.get("relationships", []):
        # Include relationships where this entity is either source or target
        if rel["from"] == entity_id or rel["to"] == entity_id:
            relationships.append(rel)

    return relationships