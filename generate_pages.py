#!/usr/bin/env python3
"""Generate entity pages dynamically during MkDocs build"""

import yaml
import mkdocs_gen_files
from pathlib import Path
import os

def load_datalink():
    """Load and parse the datalink.yaml file"""
    datalink_path = Path("data/datalink.yaml")
    if not datalink_path.exists():
        return {"entities": [], "relationships": []}
    
    with open(datalink_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

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

def main():
    """Main function to generate all entity pages"""
    # Load data
    data = load_datalink()
    
    # Generate entity pages
    for entity in data.get("entities", []):
        entity_id = entity["id"]
        page_content = generate_entity_page_content(data, entity)
        
        # Write the page using mkdocs-gen-files
        with mkdocs_gen_files.open(f"entities/{entity_id}.md", "w") as f:
            f.write(page_content)
    
    # Generate entities index page
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
    
    # Generate content by type
    for entity_type, entities in sorted(entities_by_type.items()):
        entities_index_content += f"\n### {entity_type.title()}\n\n"
        for entity in sorted(entities, key=lambda x: x["name"]):
            entities_index_content += f"- [{entity['name']}]({entity['id']}.md) - {entity.get('description', '')}\n"
    
    entities_index_content += f"\n---\n[← Back to Home](../index.md)\n"
    
    # Write the entities index page
    with mkdocs_gen_files.open("entities/index.md", "w") as f:
        f.write(entities_index_content)

# Execute main function when script is imported by mkdocs-gen-files
main()