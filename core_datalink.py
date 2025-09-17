"""
Core DataLink utilities
Shared functions for loading and manipulating DataLink data
"""

import yaml
from pathlib import Path
import glob


def load_datalink():
    """Load and parse all YAML files from data/datalink/ directory"""
    datalink_dir = Path("data/datalink")

    # Initialize combined data structure
    combined_data = {"entities": [], "relationships": []}

    # Check if new directory structure exists
    if datalink_dir.exists() and datalink_dir.is_dir():
        # Load from multiple YAML files in data/datalink/
        yaml_files = glob.glob(str(datalink_dir / "*.yaml")) + glob.glob(str(datalink_dir / "*.yml"))

        for yaml_file in sorted(yaml_files):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as file:
                    file_data = yaml.safe_load(file)
                    if file_data:
                        # Merge entities
                        if 'entities' in file_data:
                            combined_data['entities'].extend(file_data['entities'])
                        # Merge relationships
                        if 'relationships' in file_data:
                            combined_data['relationships'].extend(file_data['relationships'])
            except Exception as e:
                print(f"Warning: Could not load {yaml_file}: {e}")

    # Fallback to old single file structure
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
    """Get a specific entity by ID"""
    for entity in data.get("entities", []):
        if entity["id"] == entity_id:
            return entity
    return None


def get_entity_relationships(data, entity_id):
    """Get all relationships for a specific entity"""
    relationships = []

    for rel in data.get("relationships", []):
        if rel["from"] == entity_id or rel["to"] == entity_id:
            relationships.append(rel)

    return relationships