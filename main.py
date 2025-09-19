def define_env(env):
    """
    This is the hook for the mkdocs-macros-plugin
    """

    @env.macro
    def load_datalink():
        """Load and parse all YAML files from data/datalink/ directory"""
        from core_datalink import load_datalink as core_load_datalink
        return core_load_datalink()

    # Legacy macros - no longer needed with JSON-based entity viewer
    # @env.macro
    # def get_entity_by_id(entity_id): pass
    # @env.macro
    # def get_entity_relationships(entity_id): pass
    # @env.macro
    # def generate_entity_pages(): pass

def main():
    print("Hello from datalink!")

if __name__ == "__main__":
    main()
