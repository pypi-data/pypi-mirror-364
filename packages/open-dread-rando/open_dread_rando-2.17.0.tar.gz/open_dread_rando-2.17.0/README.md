# Open Dread Rando
Open Source randomizer patcher for Metroid Dread. Intended for use in [Randovania](https://randovania.github.io/).
Currently supports patching item pickups, starting items, and elevator/shuttle/teleportal destinations.

## Installation
`pip install open-dread-rando`

## Usage
You will need to provide JSON data matching the [JSON schema](https://github.com/randovania/open-dread-rando/blob/main/src/open_dread_rando/files/schema.json) in order to successfully patch the game. 

The patcher expects a path to an extracted romfs directory of Metroid Dread 1.0.0 or 2.1.0 as well as the desired output directory.
Output files are in a format compatible with either Atmosphere or Ryujinx, depending on the settings provided.

With a JSON file:
`python -m open_dread_rando --input-path path/to/dread/romfs --output-path path/to/the/output-mod --input-json path/to/patcher-config.json`

## Game Versions

Only versions 1.0.0 and the latest version are supported long term. Other versions might be compatible at any given point,
but new releases are free to remove that.

Currently, the following versions are supported:
- 1.0.0
- 2.1.0
