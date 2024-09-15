import json
import time
import requests

from rich.tree import Tree

from app.utils.style import Colors

class CveGithub:
    def __init__(self):
        """
        Initializes the CVEList class with the base URL for fetching CVE data 
        from the CVEProject's GitHub repository and sets default headers for requests.
        """
        self.base_url = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves"
        self.headers = {}

    def search(self, cve, title = ''):

        """
        Fetches and displays detailed information about a specific CVE from the CVE list.
        The data is retrieved from a JSON file hosted in the CVEProject's GitHub repository.

        Args:
            cve (str): The CVE ID to be searched, e.g., "CVE-2021-12345".
        """

        tree = Tree(title)
        try:
            # Convert CVE ID to uppercase
            cve = cve.upper()
            
            # Split the CVE ID to extract the year and the numeric part
            cve_year = cve.split("-")[1]

            cve_num = int(cve.split("-")[2])

            # Construct the URL for the CVE JSON file
            url = f"{self.base_url}/{cve_year}/{cve_num // 1000}xxx/{cve}.json"

            # Send the GET request to retrieve the CVE data
            response = requests.get(url, headers=self.headers)

            # Attempt to parse the response as JSON
            data = response.json()  # Raise a JSONDecodeError if the response is not valid JSON

            # Initialize Rich Console and Tree for displaying the CVE details

            # Add CVE details to the tree
            data_node = tree.add(Colors.text(data['cveMetadata']['cveId']))  # CVE ID

            data_node.add(f"Published     : {data['cveMetadata']['datePublished']}")  # Date published
            
            if data.get('containers', {}).get('cna', {}).get('metcrics'):
                data_node.add(f"Best Score    : {data['containers']['cna']['metrics'][0]['cvssV3_1']['baseScore']}")  # CVSS base score
                data_node.add(f"Vector        : {data['containers']['cna']['metrics'][0]['cvssV3_1']['vectorString']}")  # CVSS vector
            
            short_node = data_node.add("Description")
            short_node.add(data['containers']['cna']['descriptions'][0]['value'].replace('\n\n', ''))

        except requests.exceptions.RequestException as e:
            # Handle network-related errors, such as connection issues or timeouts
            tree.add(f"Error: [red]Request error: {e}[/red]")


        except json.JSONDecodeError:
            # Handle errors when the response is not a valid JSON
            tree.add(f"Error: [red]Error decoding JSON response.[/red]")

        except KeyError:
            # Handle missing keys in the JSON structure (if the CVE data is incomplete)
            tree.add(f"Error: [red]CVE data structure is incomplete or incorrect.[/red]")

        except Exception as e:

            # Catch-all for other exceptions
            if 'list index out of range' not in str(e):
                tree.add(f"Error: [red]An unexpected error occurred: {e}[/red]")
            else:
                tree.add(f"[yellow]CVE not detected[/yellow]")

        return tree
