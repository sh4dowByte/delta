import yaml
from app.config import App
from app.git_downloader import GitDownloader
from app.utils.helper import search_text_in_directory

from app.utils.style import Colors
from rich.console import Console
from rich.tree import Tree
import base64

class NucleiTemplates:
    def __init__(self):
        """Initialize Nuclei with a GitDownloader instance."""
        self.downloader = GitDownloader()
        self.path = f'{App.cache_path}/nuclei-templates-main'

    def update(self):
        """Download and extract the latest Nuclei templates from GitHub."""
        self.downloader.download_and_extract('https://github.com/projectdiscovery/nuclei-templates/archive/refs/heads/main.zip', 'Nuclei Template')

    def search(self, search_text, title = ''):
        """Search for a specific text in YAML files within the Nuclei templates directory."""
        file_path = search_text_in_directory(self.path, search_text, 'yaml')

        datas = []
        for file in file_path:
            with open(file, 'r') as yaml_file:
                outyaml = yaml.safe_load(yaml_file)
                result = outyaml.get('info')
                result['id'] = outyaml.get('id')
                
                fields_to_check = ['id', 'name', 'author', 'description', 'tags']
                for field in fields_to_check:
                    field_value = result.get(field, "")
                    # Hanya jalankan lower() jika field_value bukan None
                    if field_value and search_text.lower() in field_value.lower():
                        datas.append(result)
                        break

        tree = Tree(title)

        # Menambahkan item ke pohon
        for data in datas:
            data_node = tree.add(Colors.text(data["id"]))
            data_node.add(f"Name        : {data['name']}")
            data_node.add(f"Author      : {data['author']}")

            if data.get('severity'):
                data_node.add(f"Severity    : {self.severity_color(data['severity'])}")

            if data.get('tags'):
                data_node.add(f"Tags        : {data['tags']}")

            if data.get('impact'):
                impact_node = data_node.add(f"Impact")
                impact_node.add(data['impact'])

            if data.get('remediation'):
                data_node.add(f"Remediation : {data['remediation']}")

            if data.get('description'):
                description_node = data_node.add(f"Description")
                description_node.add(f"{data['description']}")

            if data.get('reference'):
                reference_node = data_node.add("📚 Reference")
                for ref in data['reference']:
                    reference_node.add(f"{ref}")

            if data.get('metadata', {}).get('shodan-query'):
                shodan_node = data_node.add("🌐 Shodan Query")
                if isinstance(data['metadata'].get('shodan-query'), list):
                    for ref in data['metadata']['shodan-query']:
                        shodan_node.add(f"https://www.shodan.io/search?query={ref}")
                else:
                    shodan_node.add(f"https://www.shodan.io/search?query={data['metadata'].get('shodan-query')}")
            
            if data.get('metadata', {}).get('fofa-query'):
                fofa_node = data_node.add("🌐 Fofa Query")
                if isinstance(data['metadata'].get('fofa-query'), list):
                    for ref in data['metadata']['fofa-query']:
                        fofa_node.add(f"https://en.fofa.info/result?qbase64={base64.b64encode(ref.encode("utf-8")).decode('utf-8')}")
                else:
                    query = data['metadata'].get('fofa-query')
                    query = base64.b64encode(query.encode("utf-8")).decode('utf-8')
                    fofa_node.add(f"https://en.fofa.info/result?qbase64={query}")

        if not datas:
            tree.add(f"[yellow]Exploit not detected[/yellow]")

        return tree

    def severity_color(self, severity):
        if severity == 'high':
            return Colors.text(severity, Colors.RED)
        elif severity == 'medium':
            return Colors.text(severity, Colors.YELLOW)
        elif severity == 'low':
            return Colors.text(severity, Colors.GREEN)
        elif severity == 'critical':
            return Colors.text(severity, Colors.MAGENTA)
        else:
            return Colors.text(severity, Colors.BLUE)