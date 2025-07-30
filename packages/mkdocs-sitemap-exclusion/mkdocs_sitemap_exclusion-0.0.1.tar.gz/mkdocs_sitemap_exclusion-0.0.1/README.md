# mkdocs-sitemap-exclusion
A MkDocs plugin that removes specific URLs from the generated `sitemap.xml` based on configuration settings in `mkdocs.yml`.

## Features
- Exclude URLs from the sitemap based on a specified stop word in the Markdown front matter.
- Flexible configuration options to specify additional URLs to exclude.

## Installation
You can install the plugin using pip:

```
pip install mkdocs-sitemap-exclusion
```

## Usage
To use the plugin, add it to your `mkdocs.yml` configuration file:

```yaml
plugins:
  - mkdocs-sitemap-exclusion:
      stop_word: 'exclude_from_sitemap'
      exclude:
        - '/path/to/exclude'
```

In your Markdown files, you can specify the stop word in the front matter:

```markdown
---
exclude_from_sitemap: true
---
# My Document
Content goes here.
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.