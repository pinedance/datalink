import sys
sys.path.append('.')
from core_datalink import load_datalink as core_load_datalink

def define_env(env):
    """
    MkDocs Macros Plugin Hook

    This function is called by mkdocs-macros-plugin during the build process.
    It defines macros that can be used in Markdown templates throughout the site.

    Args:
        env: The macro environment provided by mkdocs-macros-plugin
    """

    @env.macro
    def load_datalink():
        """
        Template macro for loading DataLink data in Markdown files

        This macro provides access to the complete DataLink dataset from
        within Markdown templates. It wraps the core_datalink.load_datalink()
        function to provide a clean interface for template usage.

        Returns:
            dict: Complete DataLink data structure with entities and relationships

        Usage in Markdown:
            {{ load_datalink() }}
        """
        return core_load_datalink()

def main():
    """
    Main function for standalone script execution

    This function is called when the script is run directly (not imported).
    Currently provides a simple greeting message for testing purposes.
    """
    print("Hello from datalink!")

if __name__ == "__main__":
    main()
