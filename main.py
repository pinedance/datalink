import yaml
import json
import os
from pathlib import Path

def define_env(env):
    """
    This is the hook for the mkdocs-macros-plugin
    """
    
    @env.macro
    def load_datalink():
        """Load and parse the datalink.yaml file"""
        datalink_path = Path("data/datalink.yaml")
        if not datalink_path.exists():
            return {"entities": [], "relationships": []}
        
        with open(datalink_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    @env.macro
    def generate_network_data():
        """Generate network data for vis-network.js"""
        data = load_datalink()
        
        # Create nodes
        nodes = []
        entity_colors = {
            "person": "#ff7675",
            "movie": "#74b9ff", 
            "genre": "#00b894",
            "book": "#fdcb6e",
            "music": "#a29bfe"
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
        
        # Create edges
        edges = []
        edge_colors = {
            "directed": "#e84393",
            "composed": "#00cec9", 
            "belongs_to": "#6c5ce7",
            "related_to": "#fd79a8"
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
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    @env.macro
    def get_entity_by_id(entity_id):
        """Get a specific entity by ID"""
        data = load_datalink()
        for entity in data.get("entities", []):
            if entity["id"] == entity_id:
                return entity
        return None
    
    @env.macro
    def get_entity_relationships(entity_id):
        """Get all relationships for a specific entity"""
        data = load_datalink()
        relationships = []
        
        for rel in data.get("relationships", []):
            if rel["from"] == entity_id or rel["to"] == entity_id:
                relationships.append(rel)
        
        return relationships
    
    @env.macro
    def generate_entity_pages():
        """Generate markdown content for entity detail pages"""
        data = load_datalink()
        pages = {}
        
        for entity in data.get("entities", []):
            entity_id = entity["id"]
            relationships = get_entity_relationships(entity_id)
            
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
                    content += f"- **{key.replace('_', ' ').title()}**: {', '.join(value)}\n"
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
                        from_entity = get_entity_by_id(rel["from"])
                        if from_entity:
                            content += f"- **{from_entity['name']}** {rel['type']} this entity\n"
                
                if outgoing:
                    content += "\n### Outgoing Relationships\n" 
                    for rel in outgoing:
                        to_entity = get_entity_by_id(rel["to"])
                        if to_entity:
                            content += f"- This entity {rel['type']} **{to_entity['name']}**\n"
            
            pages[entity_id] = content
        
        return pages

def main():
    print("Hello from datalink!")

if __name__ == "__main__":
    main()
