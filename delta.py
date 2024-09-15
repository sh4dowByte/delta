import argparse
import sys
import time
from app.repository.cisa import Cisa
from app.repository.cve_github import CveGithub
from app.repository.exploitdb import ExploitDB
from app.repository.first import First
from app.repository.hackerone import HackerOne
from app.repository.metasploit import Metasploit
from app.repository.nuclei_templates import NucleiTemplates
from app.repository.poc_in_github import PocInGithub
from app.utils.helper import display_banner

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

def main():
    """
    Main function to initialize and run the Delta tool. 
    It supports exploit discovery and vulnerability scanning from multiple repositories.
    """
    display_banner()

    # Initialize objects for searching
    nuclei_templates = NucleiTemplates()
    poc_in_github = PocInGithub()
    metasploit = Metasploit()
    hackerone = HackerOne()
    exploitdb = ExploitDB()
    first = First()
    cve_github = CveGithub()
    cisa = Cisa()

    # Create argument parser for handling command-line arguments
    parser = argparse.ArgumentParser(
        description="Delta - A tool for Exploit Discovery and Vulnerability Discovery Tools."
    )

    # Adding argument for the update option
    parser.add_argument(
        "--update",
        action="store_true",  # Store as boolean True if the argument is used
        help="Update the repositories for Nuclei and ExploitDB."  # Add explanation
    )

    # Adding argument for ExploitDB search
    parser.add_argument(
        "-s", "--search",
        type=str,
        help="Search for a specific term in the ExploitDB and Nuclei databases."  # Add explanation
    )

    # Parse arguments
    args = parser.parse_args()

    try:
        # Check if the update option is used
        if args.update:
            print("Updating repositories...")
            nuclei_templates.update()
            poc_in_github.update()
            metasploit.update()

        # Check if a search term is provided
        if args.search:
            # Initialize Rich console
            console = Console()

            # List of searches to perform
            search_functions = [
                (nuclei_templates.search, "📂 Nuclei Templates"),
                (poc_in_github.search, "📂 POC in GitHub"),
                (metasploit.search, "📂 Metasploit"),
                (exploitdb.search, "🌐 ExploitDB"),
                (cve_github.search, "🌐 CVE GitHub"),
                (hackerone.fetch_cwe, "🌐 CWE HackerOne"),
                (hackerone.fetch_cve, "🌐 CVE HackerOne"),
                (hackerone.fetch_cve_detail, "🌐 HackerOne Activity"),
                (cisa.search, "🌐 CISA"),

                (first.epss, "🌐 Score"), # Rank CVE
            ]

            # Display search message
            console.print(f"Searching for exploits related to: {args.search}\n\n")

            # Display loading progress
            for func, title in search_functions:
                title = f"[bold]{title}[/bold]"
                # Show loading for the current function
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                    console=console
                ) as progress:
                    task = progress.add_task(f"{title}", total=3)
                    
                    # Run the search
                    result = func(args.search, title=title)

                    console.print(result)

                    print('\n')
                    
                    # Mark the task as completed
                    progress.update(task, advance=1)

        else:
            print("No search term provided. Use -s or --search to specify a search term.")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
