import os
import sys
from pathlib import Path
from shutil import rmtree

from setuptools import Command, find_packages, setup

HERE = Path(__file__).parent


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(HERE, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(
            "{0} setup.py sdist bdist_wheel --universal".format(sys.executable)
        )

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name='mkdocs-sitemap-exclusion',
    version='0.1.0',
    description='A MkDocs plugin that removes URLs from the sitemap.xml',
    author='Dmitriy Reztsov',
    author_email='rezcov_d@mail.ru',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.4.0'
    ],
    entry_points={
        'mkdocs.plugins': [
            'mkdocs-sitemap-exclusion = mkdocs_sitemap_exclusion.plugin:ExcludeFromSitemapPlugin',
        ]
    }
)
