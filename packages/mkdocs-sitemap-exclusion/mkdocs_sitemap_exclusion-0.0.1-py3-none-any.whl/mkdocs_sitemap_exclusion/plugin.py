import os
import re
import xml.etree.ElementTree as ET

import yaml
from mkdocs.config.base import Config
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin


class ExcludePluginConfig(Config):
    exclude = Type(list, default=list())
    stop_word = Type(str, default='')


class ExcludeFromSitemapPlugin(BasePlugin[ExcludePluginConfig]):
    def _get_url_from_markdown_path(self, rel_path):
        """Convert Markdown file path to URL-style path, assuming it becomes HTML."""
        rel_url = rel_path.replace(os.sep, '/')
        if not rel_url.endswith('.md'):
            return rel_url

        rel_url = rel_url[:-2] + 'html'
        return rel_url

    def _collect_exclude_urls(self, stop_word: str, config) -> list:
        """Collects through all docs and returns list of URLs to exclude from sitemap.xml"""
        docs_dir = config['docs_dir']

        exclude_paths = set()

        for root, _, files in os.walk(docs_dir):
            for filename in files:
                if not filename.endswith('.md'):
                    continue

                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, docs_dir)
                url_path = self._get_url_from_markdown_path(rel_path)

                with open(filepath, encoding='utf-8') as f:
                    content = f.read()

                # Parse YAML front matter
                match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                if match:
                    front_matter = match.group(1)
                    try:
                        meta = yaml.safe_load(front_matter)
                        if isinstance(meta, dict) and meta.get(stop_word):
                            exclude_paths.add(url_path)
                    except yaml.YAMLError:
                        continue

        return exclude_paths

    def on_post_build(self, config):
        """
        Parse sitemap.xml and remove URLs that match 'exclude_urls'.
        Exclude list is being formed in a separate method by reading meta-information in .md files searching stop word
        defined in mkdocs.yml
        :param config: 'mkdocs.config.defaults.MkDocsConfig', dict-like object, defined in mkdocs.yml
        :return: None
        """

        sitemap_path = os.path.join(config['site_dir'], 'sitemap.xml')
        if not os.path.exists(sitemap_path):
            return

        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        stop_word = self.config.get('stop_word', '')
        exclude_urls: set = self._collect_exclude_urls(stop_word, config)
        exclude_urls.update(set(self.config.get('exclude', [])))

        for url_elem in root.findall('ns:url', ns):
            loc_elem = url_elem.find('ns:loc', ns)
            if loc_elem is not None:
                loc_text = loc_elem.text
                # Match suffix of URL (relative path)
                if any(loc_text.endswith(uri) for uri in exclude_urls):
                    root.remove(url_elem)

        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]  # Remove namespace

        # Remove xmlns attribute from root (optional, but usually wanted)
        ET.register_namespace('', '')  # this forces ElementTree not to re-insert any xmlns

        tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)


def get_plugin():
    return ExcludeFromSitemapPlugin()