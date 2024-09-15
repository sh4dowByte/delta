import re
from app.config import App
from app.git_downloader import GitDownloader
from app.utils.helper import search_text_in_directory
from app.utils.style import Colors

from rich.console import Console
from rich.tree import Tree

class Metasploit:
    def __init__(self):
        """Initialize Metasploit with a GitDownloader instance."""
        self.downloader = GitDownloader()
        self.branch = 'master'
        self.repository = 'metasploit-framework'
        self.path = f'{App.cache_path}/{self.repository}-{self.branch}'

    def update(self):
        """Download and extract the latest Metasploit from GitHub."""
        self.downloader.download_and_extract(f'https://github.com/rapid7/{self.repository}/archive/refs/heads/{self.branch}.zip', 'Metasploit', f'{self.repository}-{self.branch}/modules/')

    def search(self, search_text, title = 'Metasploit'):
        """Search for a specific text in YAML files within the Nuclei templates directory."""
        file_path = search_text_in_directory(self.path, search_text, 'rb')

        datas = []
        for file in file_path:
            with open(file, 'r') as ruby:
                content = ruby.read()

            # Variabel yang ingin diambil
            keys = ['Name', 'Description', 'Platform', 'Targets', 'Payloads', 'Author', 'References', 'DisclosureDate', 'EncoderType', 'License']

            # Mengekstrak variabel
            variables = {key: self.extract_variable(content, key) for key in keys}
            variables['path'] = file.replace(self.path+'/modules/', '').replace('.rb', '')
            # print(f"Metasploit results: {json.dumps(variables, indent=4)}")
            datas.append(variables)
            
        tree = Tree(title)

        # Menambahkan item ke pohon
        for data in datas:
            # print(json.dumps(data, indent=4))

            data_node = tree.add(Colors.text(data["path"]))

            if data.get('Author'):
                Author_node = data_node.add("👤 Author")
                if isinstance(data.get('Author'), list):
                    for ref in data['Author']:
                        Author_node.add(f"{ref}")
                else:
                    Author_node.add(f"{data['Author']}")

            data_node.add(f"Name      : {data['Name']}")

            if data.get('EncoderType'):
                data_node.add(f"Encoder   : {data['EncoderType']}")

            if data.get('License'):
                data_node.add(f"License   : {data['License']}")

            if data.get('DisclosureDate'):
                data_node.add(f"Date      : {data['DisclosureDate']}")

            if data.get('Platform'):
                data_node.add(f"Platform  : {data['Platform']}")

            if data.get('Description'):
                description_node = data_node.add(f"Description")
                cleaned_test = '\n'.join([line.lstrip() for line in data['Description'].splitlines()])
                description_node.add(f"{cleaned_test}")

        if not datas:
            tree.add(f"[yellow]Exploit not detected[/yellow]")

        return tree


    def extract_variable(self, ruby_code, key):
        # Pattern
        # 'Name'             => 'Avoid underscore/tolower',
        # or 
        # %q{ TEXT }
        pattern = rf"'{key}'\s*=>\s*(?:%q{{(.+?)}}|'(.*?)')"
        matches = re.findall(pattern, ruby_code, re.DOTALL)
        if matches:
            # Ambil nilai yang ditemukan dari hasil pencocokan
            value = matches[0][0] or matches[0][1] or matches[0][2]
            return value.strip()
        
        # Pattern 
        # 'License'          => MSF_LICENSE,
        pattern = re.compile(rf"'{key}'\s*=>\s*([\w:]+)", re.MULTILINE)
        match = pattern.search(ruby_code)
        if match:
            return match.group(1)

        # Pattern
        # 'Author'           =>
        # [
        #   'skape', # avoid_utf8_lower Author
        #   'juan vazquez' # Adapted to be usable on CVE-2012-2329
        # ],
        pattern = re.compile(rf"'{key}'\s*=>\s*\[\s*([^\]]*)\s*\]", re.MULTILINE | re.DOTALL)
        match = pattern.search(ruby_code)

        if match:
            authors_text = match.group(1)
            authors_text = re.sub(r'#.*', '', authors_text)
            authors = [author.strip().strip("'") for author in authors_text.split(',') if author.strip()]
            return (authors)
        
            
        # Regex pattern untuk menangkap array yang berada di bawah 'Targets'
        # pattern = re.compile(rf"'{key}'\s*=>\s*(\[[^\]]*\])", re.MULTILINE | re.DOTALL)

        match = pattern.search(ruby_code)
        if match:
            targets_content = match.group(1)
            return (targets_content)
        
        return None
    