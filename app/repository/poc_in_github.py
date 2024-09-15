import json
from app.config import App
from app.git_downloader import GitDownloader
from app.utils.helper import search_text_in_directory

from app.utils.style import Colors
from rich.console import Console
from rich.tree import Tree

class PocInGithub:
    def __init__(self):
        """Initialize PocInGithub with a GitDownloader instance."""
        self.downloader = GitDownloader()
        self.path = f'{App.cache_path}/PoC-in-GitHub-master'

    def update(self):
        """Download and extract the latest Poc in Github from GitHub."""
        self.downloader.download_and_extract('https://github.com/nomi-sec/PoC-in-GitHub/archive/refs/heads/master.zip', 'Poc in Github')

    def search(self, search_text, title = ''):
        """Search for a specific text in JSON files within the Poc in Github directory."""
        file_path = search_text_in_directory(self.path, search_text, 'json')

        datas = []
        for file in file_path:
            with open(file, 'r') as json_file:
                result = json.load(json_file)
                datas += result

        
        tree = Tree(title)

        for data in datas:
            data_node = tree.add(Colors.text(data['full_name']))
            data_node.add(f"Name          : {data['name']}")
            data_node.add(f"Date Publised : {data['pushed_at']}")
            data_node.add(f"Author        : {data['owner']['login']}")
            data_node.add(f"Github        : {data['html_url']}")

            if data.get('description'):
                description_node = data_node.add(f"Description")
                description_node.add(f"{data['description']}")


        if not datas:
            tree.add(f"[yellow]Exploit not detected[/yellow]")

        return tree