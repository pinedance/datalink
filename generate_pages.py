#!/usr/bin/env python3
"""Generate entity pages dynamically during MkDocs build"""

import mkdocs_gen_files
from pathlib import Path
import os
import sys

sys.path.append('.')
from core_datalink import load_datalink, get_entity_by_id, get_entity_relationships

def collect_entity_images(entity_id, entity_data):
    """Collect images from both datalink.yaml and local images folder"""
    images = []
    
    # 1. Get images from datalink.yaml
    if "image_links" in entity_data:
        for img_url in entity_data["image_links"]:
            images.append({
                "src": img_url,
                "type": "external",
                "alt": f"{entity_data['name']} image"
            })
    
    # 2. Get images from local docs/images/{entity_id}/ folder
    images_dir = Path(f"docs/images/{entity_id}")
    if images_dir.exists():
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        for img_file in images_dir.iterdir():
            if img_file.is_file() and img_file.suffix.lower() in supported_extensions:
                # Use relative path for local images
                img_path = f"/images/{entity_id}/{img_file.name}"
                images.append({
                    "src": img_path,
                    "type": "local",
                    "alt": f"{entity_data['name']} - {img_file.stem}"
                })
    
    return images

def generate_gallery_html(images):
    """Generate HTML for image gallery"""
    if not images:
        return ""
    
    gallery_html = """
## Image Gallery

<div class="image-gallery">
"""
    
    for i, img in enumerate(images):
        gallery_html += f'''
    <div class="gallery-item" data-index="{i}">
        <div class="gallery-placeholder" data-src="{img['src']}">
            <div class="placeholder-shimmer"></div>
        </div>
        <img class="gallery-image hidden" data-src="{img['src']}" alt="{img['alt']}" loading="lazy">
    </div>
'''
    
    gallery_html += """
</div>

<!-- Lightbox Modal -->
<div id="lightbox-modal" class="lightbox-modal hidden">
    <div class="lightbox-overlay"></div>
    <div class="lightbox-content">
        <button class="lightbox-close">&times;</button>
        <button class="lightbox-prev">&#8249;</button>
        <img class="lightbox-image" src="" alt="">
        <button class="lightbox-next">&#8250;</button>
        <div class="lightbox-counter">
            <span class="lightbox-current">1</span> / <span class="lightbox-total">{}</span>
        </div>
    </div>
</div>
""".format(len(images))
    
    return gallery_html

def generate_entity_page_content(data, entity):
    """Generate markdown content for a single entity"""
    entity_id = entity["id"]
    relationships = get_entity_relationships(data, entity_id)
    images = collect_entity_images(entity_id, entity)
    
    # Build relationships section
    incoming = [r for r in relationships if r["to"] == entity_id]
    outgoing = [r for r in relationships if r["from"] == entity_id]
    
    content = f"""# {entity['name']}

## Details
**Type**: {entity['type'].title()}

{entity.get('description', '')}

## Properties
"""
    
    for key, value in entity.get("properties", {}).items():
        if isinstance(value, list):
            content += f"- **{key.replace('_', ' ').title()}**: {', '.join(map(str, value))}\n"
        else:
            content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    if entity.get("external_links"):
        content += "\n## External Links\n"
        for link in entity["external_links"]:
            content += f"- [{link['name']}]({link['url']})\n"
    
    # Add image gallery
    gallery_html = generate_gallery_html(images)
    if gallery_html:
        content += gallery_html
    
    if incoming or outgoing:
        content += "\n## Relationships\n"
        
        if incoming:
            content += "\n### Incoming Relationships\n"
            for rel in incoming:
                from_entity = get_entity_by_id(data, rel["from"])
                if from_entity:
                    content += f"- **[{from_entity['name']}]({from_entity['id']}.md)** {rel['type']} this entity\n"
        
        if outgoing:
            content += "\n### Outgoing Relationships\n" 
            for rel in outgoing:
                to_entity = get_entity_by_id(data, rel["to"])
                if to_entity:
                    content += f"- This entity {rel['type']} **[{to_entity['name']}]({to_entity['id']}.md)**\n"
    
    content += f"\n---\n[← Back to Home](../index.md)\n"
    
    return content

def export_json_data(data):
    """Export data to JSON files for client-side usage"""
    import json

    # 1. Create network.json (for network graph)
    nodes = []
    entity_colors = {
        "인물": "hsla(356, 100%, 73%, 0.9)",      # 빨간색 계열 (person)
        "영화": "hsla(217, 92%, 73%, 0.9)",       # 파란색 계열 (movie)
        "장르": "hsla(162, 73%, 46%, 0.9)",       # 초록색 계열 (genre)
        "도서": "hsla(45, 93%, 70%, 0.9)",        # 노란색 계열 (book)
        "음악": "hsla(250, 85%, 75%, 0.9)",       # 보라색 계열 (music)
        "TV시리즈": "hsla(210, 11%, 45%, 0.9)",   # 회색 계열 (tv_series)
        # 영어 키 호환성 유지 (기존 데이터 지원)
        "person": "hsla(356, 100%, 73%, 0.9)",
        "movie": "hsla(217, 92%, 73%, 0.9)",
        "genre": "hsla(162, 73%, 46%, 0.9)",
        "book": "hsla(45, 93%, 70%, 0.9)",
        "music": "hsla(250, 85%, 75%, 0.9)",
        "tv_series": "hsla(210, 11%, 45%, 0.9)"
    }

    for entity in data.get("entities", []):
        nodes.append({
            "id": entity["id"],
            "label": entity["name"],
            "title": entity.get("description", ""),
            "color": entity_colors.get(entity["type"], "#636e72"),
            "shape": "dot",
            "size": 20 + len(entity.get("external_links", [])) * 5,
            "font": {"size": 14},
            "type": entity["type"]
        })

    edges = []
    edge_colors = {
        "directed": "#e84393",
        "composed": "#00cec9",
        "belongs_to": "#6c5ce7",
        "related_to": "#fd79a8",
        "starred_in": "#636e72"
    }

    for rel in data.get("relationships", []):
        edges.append({
            "from": rel["from"],
            "to": rel["to"],
            "label": rel["type"],
            "color": edge_colors.get(rel["type"], "#636e72"),
            "arrows": "to",
            "font": {"size": 12}
        })

    network_data = {"nodes": nodes, "edges": edges}
    with mkdocs_gen_files.open("data/network.json", "w") as f:
        json.dump(network_data, f, ensure_ascii=False, indent=2)

    # 2. Create entities-meta.json (for entity list)
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

    # 3. Export relationships.json
    with mkdocs_gen_files.open("data/relationships.json", "w") as f:
        json.dump(data.get("relationships", []), f, ensure_ascii=False, indent=2)

    # 4. Export individual entity detail files
    for entity in data.get("entities", []):
        entity_id = entity["id"]

        # Add local images info
        entity_detail = dict(entity)
        entity_detail["local_images"] = []

        # Check for local images
        images_dir = Path(f"docs/images/{entity_id}")
        if images_dir.exists():
            supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            for img_file in images_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in supported_extensions:
                    entity_detail["local_images"].append({
                        "filename": img_file.name,
                        "path": f"/images/{entity_id}/{img_file.name}",
                        "alt": f"{entity['name']} - {img_file.stem}"
                    })

        # Export individual entity file
        with mkdocs_gen_files.open(f"data/entities/{entity_id}.json", "w") as f:
            json.dump(entity_detail, f, ensure_ascii=False, indent=2)

def main():
    """Main function to generate all entity pages and JSON data"""
    # Load data
    data = load_datalink()

    # Export JSON data for client-side usage
    export_json_data(data)

    # Individual entity pages are now replaced by the single entity viewer
    # Keeping this code commented for reference, remove after confirming new system works
    # for entity in data.get("entities", []):
    #     entity_id = entity["id"]
    #     page_content = generate_entity_page_content(data, entity)
    #     with mkdocs_gen_files.open(f"entities/{entity_id}.md", "w") as f:
    #         f.write(page_content)

    # Generate entities index page (update links to use new entity viewer)
    entities_index_content = """# Entities

This section contains detailed pages for all entities in the DataLink system.

## Available Entities

"""

    # Group entities by type
    entities_by_type = {}
    for entity in data.get("entities", []):
        entity_type = entity["type"]
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)

    # Generate content by type - update links to use entity viewer
    for entity_type, entities in sorted(entities_by_type.items()):
        entities_index_content += f"\n### {entity_type.title()}\n\n"
        for entity in sorted(entities, key=lambda x: x["name"]):
            entities_index_content += f"- [{entity['name']}](entity.html#{entity['id']}) - {entity.get('description', '')}\n"

    entities_index_content += f"\n---\n[← Back to Home](../index.md)\n"

    # Write the entities index page
    with mkdocs_gen_files.open("entities/index.md", "w") as f:
        f.write(entities_index_content)

# Execute main function when script is imported by mkdocs-gen-files
main()