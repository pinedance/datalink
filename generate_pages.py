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

def generate_entity_pages(data):
    """
    Generate individual static pages for each entity

    Args:
        data (dict): Combined DataLink data structure with entities and relationships
    """
    relationships = data.get("relationships", [])

    for entity in data.get("entities", []):
        entity_id = entity["id"]

        # Create markdown content for the entity
        content = f"# {entity['name']}\n\n"

        # Add basic information
        content += f"**유형**: {entity['type']}\n\n"
        content += f"**설명**: {entity.get('description', 'N/A')}\n\n"

        # Add properties section
        properties = entity.get("properties", {})
        if properties:
            content += "## 상세 정보\n\n"
            for key, value in properties.items():
                if isinstance(value, list):
                    if key == "태그":
                        value_str = " ".join(f"`{tag}`" for tag in value)
                    else:
                        value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)
                content += f"- **{key}**: {value_str}\n"
            content += "\n"

        # Add relationships section
        entity_relationships = [r for r in relationships if r["from"] == entity_id or r["to"] == entity_id]
        if entity_relationships:
            content += "## 관련 정보\n\n"

            # Group relationships by type
            rel_by_type = {}
            for rel in entity_relationships:
                rel_type = rel["type"]
                if rel_type not in rel_by_type:
                    rel_by_type[rel_type] = []
                rel_by_type[rel_type].append(rel)

            for rel_type, rels in rel_by_type.items():
                type_names = {
                    "starred_in": "출연",
                    "directed": "감독",
                    "composed": "작곡",
                    "related_to": "관련",
                    "sequel": "연관작품"
                }
                type_name = type_names.get(rel_type, rel_type)
                content += f"### {type_name}\n\n"

                for rel in rels:
                    if rel["from"] == entity_id:
                        # This entity is the subject
                        target_id = rel["to"]
                        target_entity = next((e for e in data["entities"] if e["id"] == target_id), None)
                        if target_entity:
                            content += f"- [{target_entity['name']}]({target_id}.md)"
                            if rel.get("properties"):
                                props_text = []
                                for k, v in rel["properties"].items():
                                    if k not in ["역할", "캐릭터", "캐릭터설명"]:
                                        props_text.append(f"{k}: {v}")
                                if props_text:
                                    content += f" ({', '.join(props_text)})"
                            content += "\n"
                    else:
                        # This entity is the object
                        source_id = rel["from"]
                        source_entity = next((e for e in data["entities"] if e["id"] == source_id), None)
                        if source_entity:
                            content += f"- [{source_entity['name']}]({source_id}.md)"
                            if rel.get("properties"):
                                role = rel["properties"].get("역할", "")
                                if role:
                                    content += f" (역할: {role})"
                            content += "\n"
                content += "\n"

        # Add external links section
        external_links = entity.get("external_links", [])
        if external_links:
            content += "## 외부 링크\n\n"
            for link in external_links:
                name = link.get('name', 'Link')
                url = link.get('url', '#')
                content += f"- [{name}]({url})\n"
            content += "\n"

        # Add local images section
        images_dir = Path(f"docs/images/{entity_id}")
        if images_dir.exists():
            image_files = []
            supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            for img_file in images_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in supported_extensions:
                    image_files.append(img_file)

            if image_files:
                content += "## 이미지\n\n"
                for img_file in image_files:
                    content += f"![{entity['name']} - {img_file.stem}](../images/{entity_id}/{img_file.name})\n\n"

        # Add navigation
        content += "---\n\n"
        content += "[← Entities 목록으로](index.md) | [🏠 홈으로](../index.md)\n"

        # Write the entity page
        with mkdocs_gen_files.open(f"entities/{entity_id}.md", "w") as f:
            f.write(content)

def main():
    """
    Main function to generate all entity pages and JSON data

    This function orchestrates the entire build process:
    1. Loads YAML data using core_datalink module
    2. Exports JSON files for client-side consumption
    3. Generates individual static entity pages
    4. Generates the entity index page with navigation links

    Called by mkdocs-gen-files plugin during MkDocs build
    """
    # Load data from YAML files using core utilities
    data = load_datalink()

    # Export JSON data for client-side usage (network, entities, relationships)
    export_json_data(data)

    # Generate individual entity pages
    generate_entity_pages(data)

    # Generate enhanced entities index page with dashboard + card layout
    # Group entities by type for organized display
    entities_by_type = {}
    total_entities = len(data.get("entities", []))

    for entity in data.get("entities", []):
        entity_type = entity["type"]
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)

    # Type icons mapping
    type_icons = {
        "영화": "🎬",
        "TV시리즈": "📺",
        "인물": "👤",
        "작곡가": "🎵",
        "감독": "🎭"
    }

    # Load template from separate file
    template_path = "templates/entities_index.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Warning: Template file {template_path} not found. Using fallback template.")
        template_content = """# 🌐 Entities
<div class="entities-dashboard">
<h2>📊 통계 요약</h2>
<div class="stats-grid">
{category_sections}
</div>
</div>"""

    # Build category sections
    category_sections = ""

    # Add type-specific stats - first build stats cards
    stats_cards = f"""<div class="stat-card">
<strong>총 엔티티</strong><br>
<strong>{total_entities}개</strong>
</div>

"""

    for entity_type, entities in sorted(entities_by_type.items()):
        count = len(entities)
        icon = type_icons.get(entity_type, "📄")
        stats_cards += f"""<div class="stat-card">
<strong>{icon} {entity_type}</strong><br>
<strong>{count}개</strong>
</div>

"""

    # Generate card layout for each type
    for entity_type, entities in sorted(entities_by_type.items()):
        icon = type_icons.get(entity_type, "📄")
        category_sections += f"""
<h3>{icon} {entity_type}</h3>

<div class="entity-cards">

"""

        # Sort entities by name and create cards
        for entity in sorted(entities, key=lambda x: x["name"]):
            # Truncate description if too long
            description = entity.get('description', '')
            if len(description) > 100:
                description = description[:97] + "..."

            # Extract some key properties for display
            properties = entity.get('properties', {})
            meta_info = []

            if '출생년도' in properties:
                meta_info.append(f"📅 {properties['출생년도']}")
            elif '개봉년도' in properties:
                meta_info.append(f"📅 {properties['개봉년도']}")
            elif '방영년도' in properties:
                meta_info.append(f"📅 {properties['방영년도']}")
            elif '시작년도' in properties:
                meta_info.append(f"📅 {properties['시작년도']}")

            if '국적' in properties:
                meta_info.append(f"🌍 {properties['국적']}")
            elif '제작국가' in properties:
                meta_info.append(f"🌍 {properties['제작국가']}")

            if '장르' in properties and isinstance(properties['장르'], list):
                genres = properties['장르'][:2]  # Show first 2 genres
                meta_info.append(f"🎭 {', '.join(genres)}")

            meta_text = " • ".join(meta_info) if meta_info else ""

            category_sections += f"""
<div class="entity-card">
<strong><a href="{entity['id']}.html">{entity['name']}</a></strong>
<p>{description}</p>
{f"<small>{meta_text}</small>" if meta_text else ""}
</div>
"""

        category_sections += """
</div>
"""

    # Calculate stats for template replacement
    tv_count = len(entities_by_type.get("TV시리즈", []))
    movie_count = len(entities_by_type.get("영화", []))
    person_count = len(entities_by_type.get("인물", []))

    # Use template with replacements
    entities_index_content = template_content.format(
        total_count=total_entities,
        tv_count=tv_count,
        movie_count=movie_count,
        person_count=person_count,
        category_sections=category_sections
    )

    # Write the entities index page
    with mkdocs_gen_files.open("entities/index.md", "w") as f:
        f.write(entities_index_content)

# Execute main function when script is imported by mkdocs-gen-files
# This happens automatically during MkDocs build process
main()