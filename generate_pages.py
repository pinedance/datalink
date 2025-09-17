#!/usr/bin/env python3
"""Generate entity pages dynamically during MkDocs build"""

import yaml
import mkdocs_gen_files
from pathlib import Path

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

def generate_entity_page_content(data, entity):
    """Generate markdown content for a single entity"""
    entity_id = entity["id"]
    relationships = get_entity_relationships(data, entity_id)
    
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