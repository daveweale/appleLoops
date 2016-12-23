# appleLoops.py

## What does it do?
Downloads the 'core' content that is downloaded by GarageBand or Logic Pro on first run.

Useful for importing these packages into deployment tools like `munki` or `JAMF Pro`.

## GarageBand First Run Behaviour
The current version of GarageBand (10.1.4 as at 2016-12-23) does the following:
- Prompts to download approximately 2.11GB of mandatory content for basic functionality
- Prompts to download approximately 9GB of optional content for extended functionality

The mandatory content consists of 35 packages, the optional content consists of 56 packages.
