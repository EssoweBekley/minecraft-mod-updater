# Minecraft Mod Updater

This Python script automates the process of updating Minecraft mods by downloading the latest compatible versions from Modrinth based on user input. It supports specifying Minecraft versions and mod loaders/frameworks (e.g., Forge, Fabric).

## Features

- **Select a Folder**: Choose the folder containing your Minecraft mod `.jar` files.
- **Search and Download**: Automatically search for and download the latest compatible mod versions from Modrinth.
- **Framework Support**: Filter mods based on the specified loader/framework (e.g., Forge, Fabric).
- **Clean Output**: Deletes the old mods folder and creates a fresh one to store the updated mods.
- **Error Handling**: Provides detailed output on successful updates and failures.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/EssoweBekley/minecraft-mod-updater.git
    cd minecraft-mod-updater
    ```

2. **Install Dependencies**:
    Ensure you have Python installed, then install the required packages:
    ```bash
    pip install requests
    ```

## Usage

1. **Run the Script**:
    ```bash
    python mod_updater.py
    ```

2. **Follow the Prompts**:
    - Select the folder containing your Minecraft mod `.jar` files.
    - Enter the Minecraft version you want to update to (e.g., `1.19.2`).
    - Specify the mod loader/framework if known (e.g., `forge`, `fabric`), or press Enter to skip.

3. **Review the Results**:
    - The script will output the status of each mod update.
    - After completion, it will prompt you to press Enter to exit.

## Example Output

