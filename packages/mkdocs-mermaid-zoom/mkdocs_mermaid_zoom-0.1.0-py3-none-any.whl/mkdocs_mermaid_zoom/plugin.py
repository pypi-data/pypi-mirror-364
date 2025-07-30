import os
import time
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.files import File
import logging

log = logging.getLogger("mkdocs.plugins." + __name__)

class MermaidZoomPlugin(BasePlugin):
    """
    A MkDocs plugin that adds zoom, pan, and a custom lightbox to Mermaid diagrams.
    """
    config_scheme = (
        ('param_name', config_options.Type(str, default='')),
    )

    def on_files(self, files, config):
        """
        Add our plugin's assets to the file list, so they are copied to the site_dir.
        """
        plugin_dir = os.path.dirname(__file__)
        assets_src_dir = os.path.join(plugin_dir, 'assets')
        
        for filename in os.listdir(assets_src_dir):
            file = File(
                path=os.path.join('assets', filename),
                src_dir=plugin_dir,
                dest_dir=config['site_dir'],
                use_directory_urls=config['use_directory_urls']
            )
            files.append(file)
        
        return files

    def on_config(self, config):
        """
        Add our CSS and JS to the global config with a cache-busting query string.
        """
        # Create a unique version string using the current time.
        version = str(int(time.time()))

        # Define base paths for our assets.
        base_css_path = os.path.join('assets', 'mermaid-zoom.css')
        base_js_path = os.path.join('assets', 'mermaid-zoom.js')

        # Remove any old versions of our assets from the config lists.
        config['extra_css'] = [p for p in config['extra_css'] if not p.startswith(base_css_path)]
        config['extra_javascript'] = [p for p in config['extra_javascript'] if not p.startswith(base_js_path)]
        
        # Add the new versions with the cache-busting query string.
        config['extra_css'].append(f"{base_css_path}?v={version}")
        config['extra_javascript'].append(f"{base_js_path}?v={version}")
            
        return config 