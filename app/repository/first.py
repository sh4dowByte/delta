import requests
from rich.console import Console
from rich.tree import Tree

from app.utils.style import Colors

class First:
    def __init__(self):
        """
        Initialize the First class with the base URL for the FIRST API.
        The base URL is used to fetch EPSS data for a given CVE (Common Vulnerabilities and Exposures).
        """
        self.base_url = "https://api.first.org/"
        self.headers = {}
    
    def epss(self, cve, title):
        """
        Fetch EPSS (Exploit Prediction Scoring System) data for the given CVE and display it using rich tree formatting.
        
        Args:
        cve (str): The CVE ID to search for EPSS data.
        
        The function formats the API URL with the CVE, makes a request to FIRST API, 
        and then displays the patching priority based on calculated rank score.
        """

        tree = Tree(title)
        
        # Format the base URL with the CVE provided
        url = f'{self.base_url}data/v1/epss?cve={cve}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json().get('data', [])

            # Initialize console and tree for rich output

            # Iterate through each result and calculate patch priority rank
            for rank in result:
                tree.add(f"Date       : {rank['date']}")
                tree.add(f"EPSS Score : {float(rank['epss'])}")
                tree.add(f"Percentile : {float(rank['percentile'])}")

                rank_score = self.calculate_patch_rank(float(rank['epss']), float(rank['percentile']))
                summary = tree.add('📕 Summary')
                summary.add(f"Patching priority rank: {rank_score}")

            if not result:
                tree.add(f"[yellow]CVE not detected[/yellow]")

        else:
            # Optional error handling if the request fails
            tree.add(f"Error: [red]{response.status_code}[/red]")

        return tree
    
    def calculate_patch_rank(self, epss, percentile):
        """
        Calculate the patching priority rank based on the EPS and percentile.
        
        Args:
        epss (float): The Exploit Prediction Scoring System (EPSS) score.
        percentile (float): The percentile ranking of the CVE in terms of likelihood of exploitation.
        
        Returns:
        str: The priority rank as a colored string, classified into Critical, High, Medium, or Low.
        
        The patch rank is calculated by weighting both the EPS score and the percentile (70% EPS, 30% percentile). 
        Then, the rank is classified into four categories: Critical, High, Medium, and Low.
        """
        # Weighted score combining both epss and percentile
        rank_score = (epss * 0.7) + (percentile * 0.3)
        
        # Assign priority based on score thresholds
        if rank_score >= 0.8:
            return Colors.text("Critical", Colors.MAGENTA)
        elif rank_score >= 0.6:
            return Colors.text("High", Colors.RED)
        elif rank_score >= 0.4:
            return Colors.text("Medium", Colors.YELLOW)
        else:
            return Colors.text("Low", Colors.GREEN)
