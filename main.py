import json
import os

def define_env(env):
    """
    This is the hook for the mkdocs-macros-plugin
    """

    @env.macro
    def load_datalink():
        """Load and parse all YAML files from data/datalink/ directory"""
        from core_datalink import load_datalink as core_load_datalink
        return core_load_datalink()
    
    
    @env.macro
    def get_entity_by_id(entity_id):
        """Get a specific entity by ID"""
        from core_datalink import load_datalink as core_load_datalink, get_entity_by_id as core_get_entity_by_id
        data = core_load_datalink()
        return core_get_entity_by_id(data, entity_id)

    @env.macro
    def get_entity_relationships(entity_id):
        """Get all relationships for a specific entity"""
        from core_datalink import load_datalink as core_load_datalink, get_entity_relationships as core_get_entity_relationships
        data = core_load_datalink()
        return core_get_entity_relationships(data, entity_id)
    
    @env.macro
    def generate_entity_pages():
        """Generate markdown content for entity detail pages"""
        from core_datalink import load_datalink as core_load_datalink, get_entity_relationships as core_get_entity_relationships, get_entity_by_id as core_get_entity_by_id
        data = core_load_datalink()
        pages = {}

        for entity in data.get("entities", []):
            entity_id = entity["id"]
            relationships = core_get_entity_relationships(data, entity_id)

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
                        from_entity = core_get_entity_by_id(data, rel["from"])
                        if from_entity:
                            content += f"- **{from_entity['name']}** {rel['type']} this entity\n"

                if outgoing:
                    content += "\n### Outgoing Relationships\n"
                    for rel in outgoing:
                        to_entity = core_get_entity_by_id(data, rel["to"])
                        if to_entity:
                            content += f"- This entity {rel['type']} **{to_entity['name']}**\n"
            
            pages[entity_id] = content
        
        return pages

def main():
    print("Hello from datalink!")

if __name__ == "__main__":
    main()
