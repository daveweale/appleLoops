# appleLoops.py

## What does it do?
Downloads the 'core' content that is downloaded by GarageBand or Logic Pro X on first run.

## What this won't do
* Install packages
* Import packages into your package deployment system

## GarageBand first run behaviour
The current version of GarageBand (10.1.4 as at 2016-12-23) does the following:
- Prompts to download approximately 1.96GB of 'essential' content for basic functionality
- Prompts to download approximately 7.28GB of optional content for extended functionality

The 'essential' content consists of 35 packages, the optional content consists of 56 packages.

## Logic Pro X first run behaviour
The current version of Logic Pro X (10.2.4 as at 2016-11-23) has:
- Approximately 1.5GB of 'essential' content for basic functionality
- Aproximately 43.62GB of optional content available for download

The 'essential' content consists of 29 packages, the optional content consists of 557 packages.

## Usage
* `git clone https://github.com/carlashley/appleLoops`
* `./appleLoops.py --help` for usage

### Quick usage examples
* `./appleLoops.py` will download all GarageBand content (optional and mandatory)
* `./appleLoops.py --dry-run --package-set garageband --optional-only` will do a dry run for all GarageBand optional content
* `./appleLoops.py --package-set logicpro --mandatory-only` will download all essential Logic Pro X content

