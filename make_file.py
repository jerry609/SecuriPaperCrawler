import os
from pathlib import Path

# Define the directory structure as a nested dictionary
structure = {
    "agents": ["__init__.py", "base_agent.py", "research_agent.py", "code_analysis_agent.py", "quality_agent.py", "documentation_agent.py"],
    "core": ["__init__.py", "workflow.py", "context.py"],
    "utils": ["__init__.py", "logger.py", "analyzer.py", "downloader.py"],
    "config": ["__init__.py", "settings.py"]
}

# Function to create directories and files based on the structure
def create_structure(base_path, structure):
    for folder, files in structure.items():
        folder_path = Path(base_path) / folder
        folder_path.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
        for file in files:
            (folder_path / file).touch()  # Create an empty file

# Set the base directory path to D:\SecuriPaperCrawler
base_directory = "D:/SecuriPaperCrawler"  # Use / for cross-platform compatibility

# Create the directory and file structure
create_structure(base_directory, structure)

print("Directory and file structure created successfully at D:/SecuriPaperCrawler.")
