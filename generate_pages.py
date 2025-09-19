#!/usr/bin/env python3
"""
Generate JSON data files and entity index page during MkDocs build

This script is executed by mkdocs-gen-files plugin during the MkDocs build process.
It processes YAML data from the DataLink system and generates:
- JSON data files for client-side consumption
- Entity index pages with navigation links
- Network graph data for visualization

The script replaces the old system of generating individual HTML pages
with a more efficient JSON-based approach for the entity viewer.
"""

import mkdocs_gen_files
from pathlib import Path
import sys

# Add current directory to path to import core_datalink
sys.path.append('.')
from core_datalink import load_datalink

def export_json_data(data):
    """
    Export data to JSON files for client-side usage

    This function generates all the JSON files needed by the frontend:
    1. network.json - Node/edge data for vis-network graph visualization
    2. entities-meta.json - Metadata for all entities (for search/navigation)
    3. relationships.json - All relationship data for entity pages
    4. Individual entity files - Detailed data for each entity including local images

    Args:
        data (dict): Combined DataLink data structure with entities and relationships
    """
    import json

    # 1. Create network.json (for network graph visualization)
    nodes = []

    # Color mapping for different entity types
    # Uses HSL colors for consistent appearance and accessibility
    entity_colors = {
        # Korean entity types (primary)
        "인물": "hsla(356, 100%, 73%, 0.9)",      # Red tones for person
        "영화": "hsla(217, 92%, 73%, 0.9)",       # Blue tones for movie
        "장르": "hsla(162, 73%, 46%, 0.9)",       # Green tones for genre
        "도서": "hsla(45, 93%, 70%, 0.9)",        # Yellow tones for book
        "음악": "hsla(250, 85%, 75%, 0.9)",       # Purple tones for music
        "TV시리즈": "hsla(210, 11%, 45%, 0.9)",   # Gray tones for TV series
        # English keys for backward compatibility
        "person": "hsla(356, 100%, 73%, 0.9)",
        "movie": "hsla(217, 92%, 73%, 0.9)",
        "genre": "hsla(162, 73%, 46%, 0.9)",
        "book": "hsla(45, 93%, 70%, 0.9)",
        "music": "hsla(250, 85%, 75%, 0.9)",
        "tv_series": "hsla(210, 11%, 45%, 0.9)"
    }

    # Generate nodes for the network graph
    # Each entity becomes a node with visual properties based on its type and data
    for entity in data.get("entities", []):
        nodes.append({
            "id": entity["id"],
            "label": entity["name"],
            "title": entity.get("description", ""),  # Hover tooltip
            "color": entity_colors.get(entity["type"], "hsla(200, 9%, 41%, 1)"),
            "shape": "dot",
            # Dynamic size based on number of external links (more connections = larger node)
            "size": 20 + len(entity.get("external_links", [])) * 5,
            "font": {"size": 14},
            "type": entity["type"]
        })

    # Generate edges for the network graph
    edges = []

    # Color mapping for different relationship types
    edge_colors = {
        "directed": "hsla(328, 78%, 64%, 1)",      # Pink for directed relationships
        "composed": "hsla(178, 100%, 40%, 1)",     # Teal for composition relationships
        "belongs_to": "hsla(252, 69%, 63%, 1)",   # Purple for belonging relationships
        "related_to": "hsla(345, 95%, 74%, 1)",   # Light pink for general relations
        "starred_in": "hsla(200, 9%, 41%, 1)"    # Gray for starring relationships
    }

    # Convert relationships to vis-network edge format
    for rel in data.get("relationships", []):
        edges.append({
            "from": rel["from"],
            "to": rel["to"],
            "label": rel["type"],
            "color": edge_colors.get(rel["type"], "hsla(200, 9%, 41%, 1)"),
            "arrows": "to",  # Show directional arrows
            "font": {"size": 12}
        })

    # Combine nodes and edges for vis-network consumption
    network_data = {"nodes": nodes, "edges": edges}
    with mkdocs_gen_files.open("data/network.json", "w") as f:
        json.dump(network_data, f, ensure_ascii=False, indent=2)

    # 2. Create entities-meta.json (lightweight metadata for search and navigation)
    # This file contains essential info for all entities without full details
    entities_meta = {}
    for entity in data.get("entities", []):
        entities_meta[entity["id"]] = {
            "id": entity["id"],
            "name": entity["name"],
            "type": entity["type"],
            "description": entity.get("description", ""),
            "properties": entity.get("properties", {}),
            "external_links": entity.get("external_links", []),
            "image_links": entity.get("image_links", [])
        }

    with mkdocs_gen_files.open("data/entities-meta.json", "w") as f:
        json.dump(entities_meta, f, ensure_ascii=False, indent=2)

    # 3. Export relationships.json (all relationship data for entity pages)
    # This file contains the complete relationship data for filtering on entity pages
    with mkdocs_gen_files.open("data/relationships.json", "w") as f:
        json.dump(data.get("relationships", []), f, ensure_ascii=False, indent=2)

    # 4. Export individual entity detail files
    # Each entity gets its own JSON file with complete data including local images
    for entity in data.get("entities", []):
        entity_id = entity["id"]

        # Create enhanced entity data with local images
        entity_detail = dict(entity)  # Copy all original data
        entity_detail["local_images"] = []

        # Scan for local images in the docs/images/{entity_id}/ directory
        images_dir = Path(f"docs/images/{entity_id}")
        if images_dir.exists():
            # Supported image formats for the gallery
            supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            for img_file in images_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in supported_extensions:
                    entity_detail["local_images"].append({
                        "filename": img_file.name,
                        "path": f"/images/{entity_id}/{img_file.name}",
                        "alt": f"{entity['name']} - {img_file.stem}"
                    })

        # Export individual entity file for detailed viewing
        with mkdocs_gen_files.open(f"data/entities/{entity_id}.json", "w") as f:
            json.dump(entity_detail, f, ensure_ascii=False, indent=2)

def main():
    """
    Main function to generate all entity pages and JSON data

    This function orchestrates the entire build process:
    1. Loads YAML data using core_datalink module
    2. Exports JSON files for client-side consumption
    3. Generates the entity index page with navigation links

    Called by mkdocs-gen-files plugin during MkDocs build
    """
    # Load data from YAML files using core utilities
    data = load_datalink()

    # Export JSON data for client-side usage (network, entities, relationships)
    export_json_data(data)

    # Note: Individual entity pages replaced by single entity viewer system
    # This significantly reduces build time and improves maintainability

    # Generate entities index page with links to the entity viewer
    entities_index_content = """# Entities

This section contains detailed pages for all entities in the DataLink system.

## Available Entities

"""

    # Group entities by type for organized display
    entities_by_type = {}
    for entity in data.get("entities", []):
        entity_type = entity["type"]
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)

    # Generate content organized by entity type
    # Links now point to the single entity viewer with hash routing
    for entity_type, entities in sorted(entities_by_type.items()):
        entities_index_content += f"\n### {entity_type.title()}\n\n"
        for entity in sorted(entities, key=lambda x: x["name"]):
            # Use hash-based routing to the entity viewer
            entities_index_content += f"- [{entity['name']}](entity.html#{entity['id']}) - {entity.get('description', '')}\n"

    entities_index_content += f"\n---\n[← Back to Home](../index.md)\n"

    # Write the entities index page
    with mkdocs_gen_files.open("entities/index.md", "w") as f:
        f.write(entities_index_content)

# Execute main function when script is imported by mkdocs-gen-files
# This happens automatically during MkDocs build process
main()