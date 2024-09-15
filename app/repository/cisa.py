import requests
from rich.console import Console
from rich.tree import Tree

from app.utils.style import Colors

class Cisa:
    def __init__(self):
        """
        Initializes the Cisa class with the base URL for the known exploited vulnerabilities JSON feed 
        from CISA and sets default headers for requests.
        """
        self.base_url = (
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        )
        self.headers = {}
    
    def search(self, cve_id, title = ''):
        """
        Searches for a specific CVE ID or CWE in the CISA known exploited vulnerabilities database.
        If a match is found, it displays detailed information about the vulnerability using a rich tree structure.

        Args:
            cve_id (str): The CVE ID or CWE to search for in the CISA database.
        """
        url = self.base_url
        response = requests.get(url, headers=self.headers)

        # If the response is successful, process the data
        if response.status_code == 200:
            vulnerabilities = response.json()['vulnerabilities']

            # Initialize Rich Console and Tree for structured output
            tree = Tree(title)

            # Filter the vulnerabilities that match the given CVE ID or CWE
            filtered_vulnerability = [
                vuln for vuln in vulnerabilities 
                if cve_id in vuln["cveID"] or cve_id in vuln.get("cwes", [])
            ]

            # Iterate through the filtered vulnerabilities and display detailed information
            for cisa in filtered_vulnerability:
                data_node = tree.add(f"[green]{cisa["cveID"]}[/green]")  # Add CVE ID to the tree
                data_node.add(f"Name                       : {cisa['vendorProject']}")  # Vendor name
                data_node.add(f"Product                    : {cisa['product']}")  # Product name
                data_node.add(f"Vulnerability Name         : {cisa['vulnerabilityName']}")  # Vulnerability name
                data_node.add(f"Date Add                   : {cisa['dateAdded']}")  # Date when vulnerability was added
                data_node.add(f"Required Action            : {cisa['requiredAction']}")  # Required action for mitigation
                data_node.add(f"Due Date                   : {cisa['dueDate']}")  # Mitigation due date
                
                # Highlight known ransomware campaigns
                data_node.add(f"Ransomware                 : {f"[purple]{cisa['knownRansomwareCampaignUse']}[/purple]" if cisa['knownRansomwareCampaignUse'] == 'Known' else f"[yellow]{cisa['knownRansomwareCampaignUse']}[/yellow]"}")
                
                # If there are CWE references, display them
                if cisa.get('cwes'):
                    reference_node = data_node.add("CWE")  # Add a node for CWE references
                    for ref in cisa['cwes']:
                        reference_node.add(f"{ref}")  # Add each CWE to the tree

                # Add short description of the vulnerability
                short_node = data_node.add("Short Description")
                short_node.add(cisa['shortDescription'])

                # Add notes or additional information
                notes_node = data_node.add("Notes")
                notes_node.add(cisa['notes'])
                
            # If no vulnerabilities were found, notify the user
            if not filtered_vulnerability:
                tree.add(f"[yellow]CVE or CWE not detected[/yellow]")

            return tree