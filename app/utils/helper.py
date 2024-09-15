
import os

from app.config import App
from app.utils.style import Colors, TextFormat

def display_banner():
    """
    Display a banner with a version number.

    This function prints a stylized banner including a version number and a randomly chosen text
    in different colors.

    Returns:
        None
    """
    banner = rf"""
    {Colors.DARK_GREEN}
        ____       ____           
       / __ \___  / / /_____ _
      / / / / _ \/ / __/ __ `/    
     / /_/ /  __/ / /_/ /_/ /   
    /_____/\___/_/\__/\__,_/      v{App.version}
    {Colors.RESET}
                  {TextFormat.text('Exploit Discovery Tools')}
    
    """
    print(banner)
    
def search_text_in_file(file_path, search_text):
    """Search for a specific text in a single file and print the line number where it is found."""
    found = False
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if search_text in line:
                # print(f"Found '{search_text}' in {file_path} on line {line_number}")
                found = True

    return found

def search_text_in_directory(directory_path, search_text, extension = 'yaml'):
    """Search for a specific text in all .yaml files within a directory and its subdirectories."""
    found = []
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.'+extension):
                file_path = os.path.join(root, file_name)
                search = search_text_in_file(file_path, search_text)

                if search:
                    found.append(file_path)

    return found
