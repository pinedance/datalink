#!/usr/bin/env python3
"""
Generate JSON data files and entity pages during MkDocs build

This script processes YAML data from the DataLink system and generates:
- JSON data files for client-side consumption
- Static entity pages with navigation and content
- Network graph data for visualization
"""

import mkdocs_gen_files
from pathlib import Path
import json
import sys

# Add current directory to path to import core_datalink
sys.path.append('.')
from core_datalink import load_datalink, get_entity_relationships, create_entity_lookup, get_entity_images

# Configuration constants
CONFIG = {
    'image_extensions': {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
    'colors': {
        'entities': {
            "인물": "hsla(356, 100%, 73%, 0.9)", "영화": "hsla(217, 92%, 73%, 0.9)",
            "TV시리즈": "hsla(210, 11%, 45%, 0.9)", "음악": "hsla(250, 85%, 75%, 0.9)",
            "도서": "hsla(45, 93%, 70%, 0.9)", "장르": "hsla(162, 73%, 46%, 0.9)",
            # English compatibility
            "person": "hsla(356, 100%, 73%, 0.9)", "movie": "hsla(217, 92%, 73%, 0.9)",
            "tv_series": "hsla(210, 11%, 45%, 0.9)", "music": "hsla(250, 85%, 75%, 0.9)",
            "book": "hsla(45, 93%, 70%, 0.9)", "genre": "hsla(162, 73%, 46%, 0.9)"
        },
        'relationships': {
            "directed": "hsla(328, 78%, 64%, 1)", "composed": "hsla(178, 100%, 40%, 1)",
            "belongs_to": "hsla(252, 69%, 63%, 1)", "related_to": "hsla(345, 95%, 74%, 1)",
            "starred_in": "hsla(200, 9%, 41%, 1)"
        }
    },
    'icons': {
        'types': {"인물": "👤", "영화": "🎬", "TV시리즈": "📺", "음악": "🎵", "도서": "📚", "작곡가": "🎵", "감독": "🎭"},
        'properties': {
            **{k: "📅" for k in ["출생년도", "개봉년도", "방영년도", "시작년도"]},
            **{k: "🌍" for k in ["국적", "제작국가"]},
            "출생지": "📍", "직업": "💼", "장르": "🎭", "감독": "🎬", "학력": "🎓",
            "수상": "🏆", "신장": "📏", "언어": "🗣️", "대표작": "⭐", "특기": "✨",
            "소속사": "🏢", "상영시간": "⏱️", "총회수": "📺", "방송사": "📡"
        },
        'relationships': {
            "starred_in": "🎬 출연", "directed": "🎭 감독", "composed": "🎵 작곡",
            "related_to": "🔗 관련", "sequel": "📝 연관작품"
        }
    }
}


# ImageProcessor moved to core_datalink.py


class TemplateLoader:
    """Handle template loading and caching"""

    _cache = {}

    @classmethod
    def load(cls, template_path):
        """Load template content with caching"""
        if template_path not in cls._cache:
            full_path = f"templates/{template_path}.html"
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    cls._cache[template_path] = f.read()
            except FileNotFoundError:
                print(f"Warning: Template file {full_path} not found.")
                cls._cache[template_path] = ""

        return cls._cache[template_path]


class JSONExporter:
    """Handle JSON data export"""

    @staticmethod
    def export_network_data(entities, relationships):
        """Export network.json for graph visualization"""
        nodes = [{
            "id": e["id"], "label": e["name"], "title": e.get("description", ""),
            "color": CONFIG['colors']['entities'].get(e["type"], "hsla(200, 9%, 41%, 1)"),
            "shape": "dot", "size": 20 + len(e.get("external_links", [])) * 5,
            "font": {"size": 14}, "type": e["type"]
        } for e in entities]

        edges = [{
            "from": r["from"], "to": r["to"], "label": r["type"],
            "color": CONFIG['colors']['relationships'].get(r["type"], "hsla(200, 9%, 41%, 1)"),
            "arrows": "to", "font": {"size": 12}
        } for r in relationships]

        network_data = {"nodes": nodes, "edges": edges}
        with mkdocs_gen_files.open("data/network.json", "w") as f:
            json.dump(network_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_entities_meta(entities):
        """Export entities-meta.json for search and navigation"""
        entities_meta = {e["id"]: {k: e.get(k, {} if k in ["properties"] else [])
                                   for k in ["id", "name", "type", "description", "properties", "external_links", "image_links"]}
                         for e in entities}

        with mkdocs_gen_files.open("data/entities-meta.json", "w") as f:
            json.dump(entities_meta, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_relationships(relationships):
        """Export relationships.json"""
        with mkdocs_gen_files.open("data/relationships.json", "w") as f:
            json.dump(relationships, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_entity_details(entities):
        """Export individual entity detail files with local images"""
        for entity in entities:
            entity_id = entity["id"]
            entity_detail = dict(entity)

            # Add local images data
            images = get_entity_images(entity_id, entity["name"], entity.get("image_links", []))
            entity_detail["local_images"] = [img for img in images if img["type"] == "local"]

            with mkdocs_gen_files.open(f"data/entities/{entity_id}.json", "w") as f:
                json.dump(entity_detail, f, ensure_ascii=False, indent=2)


class EntityPageGenerator:
    """Generate static entity pages"""

    def __init__(self):
        # Load all templates once
        self.templates = {
            'entity': TemplateLoader.load("entities/entity"),
            'properties': TemplateLoader.load("entities/sections/properties"),
            'property_item': TemplateLoader.load("entities/sections/property_item"),
            'relationships': TemplateLoader.load("entities/sections/relationships"),
            'relationship_type': TemplateLoader.load("entities/sections/relationship_type"),
            'external_links': TemplateLoader.load("entities/sections/external_links"),
            'local_images': TemplateLoader.load("entities/sections/local_images")
        }

    def generate_properties_section(self, properties):
        """Generate properties HTML section"""
        if not properties:
            return ""

        def format_value(key, value):
            if isinstance(value, list):
                if key == "태그":
                    return '<div class="property-tags">' + "".join(f'<span class="property-tag">{tag}</span>' for tag in value) + '</div>'
                elif key in ["대표작", "수상", "언어", "특기"]:
                    return '<div class="property-list-items">' + "".join(f'<span class="property-list-item">{v}</span>' for v in value) + '</div>'
                else:
                    return ", ".join(str(v) for v in value)
            return str(value)

        property_items = "".join(
            self.templates['property_item'].format(
                icon=CONFIG['icons']['properties'].get(key, "ℹ️"),
                key=key,
                value=format_value(key, value)
            ) for key, value in properties.items()
        )

        return self.templates['properties'].format(property_items=property_items)

    def generate_relationships_section(self, entity_id, data, entities_lookup):
        """Generate relationships HTML section"""
        entity_relationships = get_entity_relationships(data, entity_id)

        if not entity_relationships:
            return ""

        # Group by relationship type
        rel_by_type = {}
        for rel in entity_relationships:
            rel_type = rel["type"]
            if rel_type not in rel_by_type:
                rel_by_type[rel_type] = []
            rel_by_type[rel_type].append(rel)

        relationship_types = ""

        for rel_type, rels in rel_by_type.items():
            type_name = CONFIG['icons']['relationships'].get(rel_type, f"📄 {rel_type}")

            relationship_items = "".join(
                f'<li class="relationship-item"><a href="{entity["id"]}.html">{entity["name"]}</a>{self._get_relationship_meta_info(rel, "outgoing" if rel["from"] == entity_id else "incoming")}</li>\n'
                for rel in rels
                for entity_key in [rel["to"] if rel["from"] == entity_id else rel["from"]]
                if (entity := entities_lookup.get(entity_key))
            )

            relationship_types += self.templates['relationship_type'].format(
                type_name=type_name,
                relationship_items=relationship_items
            )

        return self.templates['relationships'].format(
            relationship_types=relationship_types
        )

    def _get_relationship_meta_info(self, rel, direction):
        """Get relationship metadata for display"""
        meta_info = ""
        if rel.get("properties"):
            if direction == "outgoing":
                props_text = []
                for k, v in rel["properties"].items():
                    if k not in ["역할", "캐릭터", "캐릭터설명"]:
                        props_text.append(f"{k}: {v}")
                if props_text:
                    meta_info = f'<span class="relationship-meta">{", ".join(props_text)}</span>'
            else:
                role = rel["properties"].get("역할", "")
                if role:
                    meta_info = f'<span class="relationship-meta">역할: {role}</span>'
        return meta_info

    def generate_external_links_section(self, external_links):
        """Generate external links HTML section"""
        if not external_links:
            return ""

        external_link_items = "".join(
            f'<li class="external-link-item"><a href="{link.get("url", "#")}" target="_blank" rel="noopener">{link.get("name", "Link")}</a></li>\n'
            for link in external_links
        )

        return self.templates['external_links'].format(external_link_items=external_link_items)

    def generate_images_section(self, entity_id, entity_name, image_links):
        """Generate images gallery HTML section"""
        all_images = get_entity_images(entity_id, entity_name, image_links)

        if not all_images:
            return self.templates['local_images'].format(
                image_items='<div class="no-images-message"><div class="no-images-icon">🖼️</div><p>이 엔티티에는 현재 이미지가 없습니다.</p></div>'
            )

        image_items = "".join(
            f'<div class="gallery-item" data-src="{img["src"]}" data-type="{img["type"]}">'
            f'<img class="gallery-image" src="{img["src"]}" alt="{img["alt"]}" loading="lazy">'
            f'{"<span class=\"image-source\">" + img["source"] + "</span>" if img["type"] == "linked" else ""}'
            f'</div>\n'
            for img in all_images
        )

        return self.templates['local_images'].format(image_items=image_items)

    def generate_entity_page(self, entity, data, entities_lookup):
        """Generate complete entity page"""
        entity_id, entity_name, entity_type = entity["id"], entity["name"], entity['type']

        # Create frontmatter for tags
        frontmatter = ""
        if tags := entity.get("tags", []):
            frontmatter = f"---\ntags:\n" + "".join(f"  - {tag}\n" for tag in tags) + "---\n\n"

        # Generate final content
        return self.templates['entity'].format(
            frontmatter=frontmatter,
            entity_name=entity_name,
            type_icon=CONFIG['icons']['types'].get(entity_type, "📄"),
            entity_type=entity_type,
            description=entity.get('description', 'N/A'),
            properties_section=self.generate_properties_section(entity.get("properties", {})),
            relationships_section=self.generate_relationships_section(entity_id, data, entities_lookup),
            external_links_section=self.generate_external_links_section(entity.get("external_links", [])),
            local_images_section=self.generate_images_section(entity_id, entity_name, entity.get("image_links", []))
        )

    def generate_all_entity_pages(self, data):
        """Generate all entity pages"""
        entities = data.get("entities", [])
        entities_lookup = create_entity_lookup(entities)

        for entity in entities:
            content = self.generate_entity_page(entity, data, entities_lookup)
            with mkdocs_gen_files.open(f"entities/{entity['id']}.md", "w") as f:
                f.write(content)


class IndexPageGenerator:
    """Generate entities index page"""

    @staticmethod
    def generate_index_page(entities):
        """Generate entities index page with stats and cards"""
        # Group entities by type
        entities_by_type = {}
        total_entities = len(entities)

        for entity in entities:
            entity_type = entity["type"]
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)

        # Load template
        tpl_entities_index = TemplateLoader.load("entities/index")
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

        for entity_type, type_entities in sorted(entities_by_type.items()):
            icon = CONFIG['icons']['types'].get(entity_type, "📄")
            category_sections += f"\n<h3>{icon} {entity_type}</h3>\n\n<div class=\"entity-cards\">\n\n"

            for entity in sorted(type_entities, key=lambda x: x["name"]):
                # Extract meta info efficiently
                props = entity.get('properties', {})
                meta_info = [
                    next((f"📅 {props[k]}" for k in ['출생년도', '개봉년도', '방영년도', '시작년도'] if k in props), None),
                    next((f"🌍 {props[k]}" for k in ['국적', '제작국가'] if k in props), None),
                    f"🎭 {', '.join(props['장르'][:2])}" if isinstance(props.get('장르'), list) else None
                ]
                meta_text = " • ".join(filter(None, meta_info))

                desc = entity.get('description', '')
                description = desc[:97] + "..." if len(desc) > 100 else desc

                category_sections += f'''
<div class="entity-card">
<strong><a href="{entity['id']}.html">{entity['name']}</a></strong>
<p>{description}</p>
{f"<small>{meta_text}</small>" if meta_text else ""}
</div>
'''

            category_sections += "\n</div>\n"

        # Calculate stats
        tv_count = len(entities_by_type.get("TV시리즈", []))
        movie_count = len(entities_by_type.get("영화", []))
        person_count = len(entities_by_type.get("인물", []))

        # Generate final content
        entities_index_content = tpl_entities_index.format(
            total_count=total_entities,
            tv_count=tv_count,
            movie_count=movie_count,
            person_count=person_count,
            category_sections=category_sections
        )

        with mkdocs_gen_files.open("entities/index.md", "w") as f:
            f.write(entities_index_content)


def main():
    """
    Main function to generate all entity pages and JSON data

    Orchestrates the entire build process:
    1. Load YAML data using core_datalink module
    2. Export JSON files for client-side consumption
    3. Generate individual static entity pages
    4. Generate the entity index page
    """
    # Load data from YAML files
    data = load_datalink()
    entities = data.get("entities", [])
    relationships = data.get("relationships", [])

    # Export JSON data for client-side usage
    JSONExporter.export_network_data(entities, relationships)
    JSONExporter.export_entities_meta(entities)
    JSONExporter.export_relationships(relationships)
    JSONExporter.export_entity_details(entities)

    # Generate individual entity pages
    page_generator = EntityPageGenerator()
    page_generator.generate_all_entity_pages(data)

    # Generate entities index page
    IndexPageGenerator.generate_index_page(entities)


# Execute main function when script is imported by mkdocs-gen-files
if __name__ == "__main__":
    main()
else:
    main()