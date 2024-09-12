import os
import shutil
import zipfile
import json
import tkinter as tk
from tkinter import filedialog
import requests

class OpenFolder:
    def __init__(self):
        pass

    def select_folder(self):
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Select your Minecraft mods folder")
        if folder_path:
            return folder_path
        else:
            print("No folder selected.")
            return None

    def read_mod_folder(self, folder_path):
        mod_files = os.listdir(folder_path)
        mods = []
        for file in mod_files:
            if file.endswith(".jar"):
                mod_name = os.path.splitext(file)[0]
                mods.append(os.path.join(folder_path, file))  # Return full path
        return mods

class ModrinthUpdater:
    def __init__(self):
        self.successfully_updated = set()
        self.failed_updates = []
        self.downloaded_files = set()

    def search_mod_by_name(self, mod_name, game_version=None):
        search_url = f"https://api.modrinth.com/v2/search?query={mod_name}"
        if game_version:
            search_url += f"&game_versions={game_version}"
        
        response = requests.get(search_url)
        if response.status_code == 200:
            search_results = response.json()['hits']
            return search_results
        else:
            self.failed_updates.append((mod_name, f"Error while searching for the mod. Status code: {response.status_code}"))
            return None

    def get_mod_versions(self, mod_id):
        versions_url = f"https://api.modrinth.com/v2/project/{mod_id}/version"
        response = requests.get(versions_url)
        if response.status_code == 200:
            return response.json()
        else:
            self.failed_updates.append((mod_id, f"Error retrieving mod versions. Status code: {response.status_code}"))
            return None

    def filter_versions_by_minecraft(self, versions, target_version):
        return [version for version in versions if target_version in version['game_versions']]

    def filter_versions_by_loader(self, versions, loader):
        if not loader:
            return versions  # If no specific loader is provided, return all versions
        return [version for version in versions if loader in version['loaders']]

    def extract_mod_name_from_json(self, jar_file_path):
        with zipfile.ZipFile(jar_file_path, 'r') as jar:
            try:
                with jar.open('fabric.mod.json') as json_file:
                    json_data = json.load(json_file)
                    return json_data.get('name', 'Unknown Mod Name')
            except KeyError:
                return 'Unknown Mod Name'

    def download_mod(self, mod_url, save_path):
        if save_path in self.downloaded_files:
            return True
        
        try:
            response = requests.get(mod_url)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                self.downloaded_files.add(save_path)
                
                print(f"Downloaded mod to: {save_path}")
                return True
            else:
                self.failed_updates.append((save_path, f"Failed to download mod. Status code: {response.status_code}"))
                return False
        except Exception as e:
            self.failed_updates.append((save_path, f"An error occurred while downloading mod: {e}"))
            return False

    def process_mods(self, mods, target_version, loader=None):
        mods_folder = os.path.join(os.getcwd(), 'mods')
        
        # Check if the folder exists and delete it if it does
        if os.path.exists(mods_folder):
            shutil.rmtree(mods_folder)
        
        # Create a new mods folder
        os.makedirs(mods_folder, exist_ok=True)  # Ensure the 'mods' folder exists

        for mod_path in mods:
            mod_name = self.extract_mod_name_from_json(mod_path)
            search_results = self.search_mod_by_name(mod_name, game_version=target_version)
            
            if search_results:
                selected_mod = search_results[0]  # Automatically select the first search result
                
                mod_id = selected_mod['project_id']
                
                versions = self.get_mod_versions(mod_id)
                
                if versions:
                    filtered_versions = self.filter_versions_by_minecraft(versions, target_version)
                    
                    if filtered_versions:
                        filtered_versions = self.filter_versions_by_loader(filtered_versions, loader)
                        
                        if filtered_versions:
                            # Select the latest version
                            selected_version = filtered_versions[-1]
                            
                            # Download the selected version
                            mod_url = selected_version['files'][0]['url']  # Assuming the first file is the mod file
                            file_name = f"{mod_name}-{selected_version['version_number']}.jar"
                            save_path = os.path.join(mods_folder, file_name)
                            
                            self.successfully_updated.add(mod_name)  # Add to successfully updated list

                            if not self.download_mod(mod_url, save_path):
                                print(f"Failed to download {mod_name}")
                        else:
                            self.failed_updates.append((mod_name, f"No compatible versions found for Minecraft {target_version} with loader/framework '{loader}'."))
                    else:
                        self.failed_updates.append((mod_name, f"No Minecraft {target_version} versions found."))
                else:
                    self.failed_updates.append((mod_name, "Failed to retrieve versions."))
            else:
                self.failed_updates.append((mod_name, "No search results found."))

    def print_summary(self):
        print("\nSuccessfully updated:")
        for mod in sorted(self.successfully_updated):
            print(f"- {mod}")

        if self.failed_updates:
            print("\nFailed to update:")
            for mod_name, reason in self.failed_updates:
                print(f"- {mod_name}: {reason}")

        input("\nPress Enter to exit...")

def main():
    folder_opener = OpenFolder()
    updater = ModrinthUpdater()
    
    folder_path = folder_opener.select_folder()

    print("--------------------------------NOTE-----------------------------------")
    print("Some mod creators do not specify subversions. \nAs a result, the program might indicate that no compatible versions are available.")
    print("You may need to use versions without subversions, e.g., 1.21 instead of 1.21.1.")
    print("Be aware that using versions without subversions could lead to potential incompatibilities.")
    print("To avoid issues, you may wish to manually download mods if needed.")
    print("-----------------------------------------------------------------------")
    
    if folder_path:
        mods = folder_opener.read_mod_folder(folder_path)
        if mods:
            target_version = input("Enter the Minecraft version to update your mods for (e.g., 1.19.2): ")
            loader = input("Enter the mod loader/framework (forge, fabric, etc.) if known, or press Enter to skip: ").strip().lower()
            if loader not in [None, 'forge', 'fabric', 'neoforge']:
                print("Invalid framework. Exiting.")
                return
            
            updater.process_mods(mods, target_version, loader=loader)
            updater.print_summary()
        else:
            print("No valid mod files found in the selected folder.")

if __name__ == "__main__":
    main()
