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

def load_template(template_path):
    """
    Load template content from templates directory

    Args:
        template_path (str): Path to the template file (e.g., "entities/index" or "entities/sections/properties")

    Returns:
        str: Template content
    """
    full_path = f"templates/{template_path}.html"
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Template file {full_path} not found.")
        return ""

def generate_entity_pages(data):
    """
    Generate individual static pages for each entity using templates

    Args:
        data (dict): Combined DataLink data structure with entities and relationships
    """
    relationships = data.get("relationships", [])

    # Load templates
    tpl_entities_entity = load_template("entities/entity")
    tpl_entities_sections_properties = load_template("entities/sections/properties")
    tpl_entities_sections_property_item = load_template("entities/sections/property_item")
    tpl_entities_sections_relationships = load_template("entities/sections/relationships")
    tpl_entities_sections_relationship_type = load_template("entities/sections/relationship_type")
    tpl_entities_sections_external_links = load_template("entities/sections/external_links")
    tpl_entities_sections_local_images = load_template("entities/sections/local_images")

    for entity in data.get("entities", []):
        entity_id = entity["id"]
        entity_name = entity["name"]
        entity_type = entity['type']
        description = entity.get('description', 'N/A')

        # Create frontmatter for tags
        tags = entity.get("tags", [])
        if tags:
            frontmatter = "---\n"
            frontmatter += "tags:\n"
            for tag in tags:
                frontmatter += f"  - {tag}\n"
            frontmatter += "---\n\n"
        else:
            frontmatter = ""

        # Add type icon based on entity type
        type_icons = {
            "인물": "👤",
            "영화": "🎬",
            "TV시리즈": "📺",
            "음악": "🎵",
            "도서": "📚"
        }
        type_icon = type_icons.get(entity_type, "📄")

        # Generate properties section
        properties_section = ""
        properties = entity.get("properties", {})
        if properties:
            property_items = ""

            # Add icons for common properties
            property_icons = {
                "출생년도": "📅",
                "개봉년도": "📅",
                "방영년도": "📅",
                "국적": "🌍",
                "제작국가": "🌍",
                "출생지": "📍",
                "직업": "💼",
                "장르": "🎭",
                "감독": "🎬",
                "학력": "🎓",
                "수상": "🏆",
                "신장": "📏",
                "언어": "🗣️",
                "대표작": "⭐",
                "특기": "✨",
                "소속사": "🏢",
                "상영시간": "⏱️",
                "총회수": "📺",
                "방송사": "📡"
            }

            for key, value in properties.items():
                icon = property_icons.get(key, "ℹ️")

                if isinstance(value, list):
                    if key == "태그":
                        value_str = '<div class="property-tags">' + "".join(f'<span class="property-tag">{tag}</span>' for tag in value) + '</div>'
                    elif key in ["대표작", "수상", "언어", "특기"]:
                        value_str = '<div class="property-list-items">' + "".join(f'<span class="property-list-item">{v}</span>' for v in value) + '</div>'
                    else:
                        value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)

                property_items += tpl_entities_sections_property_item.format(
                    icon=icon,
                    key=key,
                    value=value_str
                )

            properties_section = tpl_entities_sections_properties.format(
                property_items=property_items
            )

        # Generate relationships section
        relationships_section = ""
        entity_relationships = [r for r in relationships if r["from"] == entity_id or r["to"] == entity_id]
        if entity_relationships:
            # Group relationships by type
            rel_by_type = {}
            for rel in entity_relationships:
                rel_type = rel["type"]
                if rel_type not in rel_by_type:
                    rel_by_type[rel_type] = []
                rel_by_type[rel_type].append(rel)

            relationship_types = ""
            for rel_type, rels in rel_by_type.items():
                type_names = {
                    "starred_in": "🎬 출연",
                    "directed": "🎭 감독",
                    "composed": "🎵 작곡",
                    "related_to": "🔗 관련",
                    "sequel": "📝 연관작품"
                }
                type_name = type_names.get(rel_type, f"📄 {rel_type}")

                relationship_items = ""
                for rel in rels:
                    if rel["from"] == entity_id:
                        # This entity is the subject
                        target_id = rel["to"]
                        target_entity = next((e for e in data["entities"] if e["id"] == target_id), None)
                        if target_entity:
                            meta_info = ""
                            if rel.get("properties"):
                                props_text = []
                                for k, v in rel["properties"].items():
                                    if k not in ["역할", "캐릭터", "캐릭터설명"]:
                                        props_text.append(f"{k}: {v}")
                                if props_text:
                                    meta_info = f'<span class="relationship-meta">{", ".join(props_text)}</span>'

                            relationship_items += f'<li class="relationship-item"><a href="{target_id}.html">{target_entity["name"]}</a>{meta_info}</li>\n'
                    else:
                        # This entity is the object
                        source_id = rel["from"]
                        source_entity = next((e for e in data["entities"] if e["id"] == source_id), None)
                        if source_entity:
                            meta_info = ""
                            if rel.get("properties"):
                                role = rel["properties"].get("역할", "")
                                if role:
                                    meta_info = f'<span class="relationship-meta">역할: {role}</span>'

                            relationship_items += f'<li class="relationship-item"><a href="{source_id}.html">{source_entity["name"]}</a>{meta_info}</li>\n'

                relationship_types += tpl_entities_sections_relationship_type.format(
                    type_name=type_name,
                    relationship_items=relationship_items
                )

            relationships_section = tpl_entities_sections_relationships.format(
                relationship_types=relationship_types
            )

        # Generate external links section
        external_links_section = ""
        external_links = entity.get("external_links", [])
        if external_links:
            external_link_items = ""
            for link in external_links:
                name = link.get('name', 'Link')
                url = link.get('url', '#')
                external_link_items += f'<li class="external-link-item"><a href="{url}" target="_blank" rel="noopener">{name}</a></li>\n'

            external_links_section = tpl_entities_sections_external_links.format(
                external_link_items=external_link_items
            )

        # Generate images section (both local and linked images)
        local_images_section = ""
        all_images = []

        # 1. Collect local images
        images_dir = Path(f"docs/images/{entity_id}")
        if images_dir.exists():
            supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            for img_file in images_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in supported_extensions:
                    all_images.append({
                        "type": "local",
                        "src": f"../images/{entity_id}/{img_file.name}",
                        "alt": f"{entity['name']} - {img_file.stem}",
                        "description": img_file.stem.replace('_', ' ').title()
                    })

        # 2. Collect image links from YAML
        image_links = entity.get("image_links", [])
        for img_link in image_links:
            if img_link.get("url"):
                all_images.append({
                    "type": "linked",
                    "src": img_link["url"],
                    "alt": f"{entity['name']} - {img_link.get('description', 'Image')}",
                    "description": img_link.get('description', 'External image'),
                    "source": img_link.get('source', 'External')
                })

        # 3. Generate gallery HTML
        if all_images:
            image_items = ""
            for idx, img in enumerate(all_images):
                source_badge = ""
                if img["type"] == "linked":
                    source_badge = f'<span class="image-source">{img["source"]}</span>'

                image_items += f'''<div class="gallery-item" data-src="{img["src"]}" data-type="{img["type"]}">
    <img class="gallery-image" src="{img["src"]}" alt="{img["alt"]}" loading="lazy">
    {source_badge}
</div>
'''

            local_images_section = tpl_entities_sections_local_images.format(
                image_items=image_items
            )
        else:
            # No images available - show message
            no_images_message = '''<div class="no-images-message">
    <div class="no-images-icon">🖼️</div>
    <p>이 엔티티에는 현재 이미지가 없습니다.</p>
</div>'''

            local_images_section = tpl_entities_sections_local_images.format(
                image_items=no_images_message
            )

        # Generate final content using main template
        content = tpl_entities_entity.format(
            frontmatter=frontmatter,
            entity_name=entity_name,
            type_icon=type_icon,
            entity_type=entity_type,
            description=description,
            properties_section=properties_section,
            relationships_section=relationships_section,
            external_links_section=external_links_section,
            local_images_section=local_images_section
        )

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
    tpl_entities_index = load_template("entities/index")
    if not tpl_entities_index:
        print("Using fallback template for entities index.")
        tpl_entities_index = """# 🌐 Entities
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
    entities_index_content = tpl_entities_index.format(
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