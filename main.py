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
    def generate_network_data():
        """Generate network data for vis-network.js"""
        data = load_datalink()
        
        # Create nodes
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
        
        # Create edges
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
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
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
