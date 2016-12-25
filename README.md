# appleLoops.py

## What does it do?
This utility can download all the essential content required by GarageBand, Logic Pro X, and MainStage, as well as optional content that is available for the same apps.

**You are responsible for being appropriately licsened for any/all content downloaded with this tool.**

## What this won't do
* Install packages
* Import packages into your package deployment system
* Download content for older versions of GarageBand, Logic Pro X, and MainStage.

## Requirements
macOS with the system standard `python`.

## GarageBand first run behaviour
The current version of GarageBand (10.1.4 as at 2016-12-23) does the following:
- Prompts to download approximately 1.96GB of 'essential' content for basic functionality
- Prompts to download approximately 7.28GB of optional content for extended functionality

The 'essential' content consists of 35 packages, the optional content consists of 56 packages.

## Logic Pro X first run behaviour
The current version of Logic Pro X (10.2.4 as at 2016-11-23) has:
- Approximately 1.5GB of 'essential' content for basic functionality
- Aproximately 43.62GB of optional content available for download

## MainStage 3 first run behaviour
The current version of MainStage 3 (3.2.4 as at 2016-11-23) has:
- Approximately 1.68GB of 'essential' content for basic functionality
- Aproximately 43.31GB of optional content available for download

The 'essential' content consists of 35 packages, the optional content consists of 547 packages.

## Usage
* `git clone https://github.com/carlashley/appleLoops`
* `./appleLoops.py --help` for usage

### Quick usage examples
* `./appleLoops.py` will download all GarageBand content (optional and mandatory)
* `./appleLoops.py --dry-run --package-set garageband --optional-only` will do a dry run for all GarageBand optional content
* `./appleLoops.py --package-set logicpro --mandatory-only` will download all essential Logic Pro X content
* `./appleLoops.py --package-set mainstage --cache-server http://cache_server:port --destination ~/Desktop/loops` will download all MainStage content through the specified caching server, and store packages in the `~/Desktop/loops` folder.

## Behaviour

### Proxies
Untested - if there are issues with using this to download the content whilst behind a proxy, try downloading outside of the content, or if you can contribute some code to improve that behaviour, please feel free to create a pull request.

### Package download location
* Defaults to `/tmp/appleLoops` with subfolders for `garageband` and `logicpro`.
* Mandatory/optional content gets saved into `YYYY/mandatory` or `YYYY/optional`

Example for GarageBand content:
`/tmp/appleLoops/garageband/2016/mandatory`

Download path can be overriden with the `-d <folder>` or `--destination <folder>` option. If the folder doesn't exist, it gets created (make sure you have permission to create directories in the specified destination).

Subfolder heirarchy remains the same.

### Duplicate content
Where a package from one app is used in another app, if a local copy already exists in other folders, copy that into the new location instead of downloading it again.

### Resume downloads
Where possible, downloads are resumed (incomplete files are over-written).

### Resume copies
Tested behaviour indicates if a local copy already exists, and the new file doesn't or only partially exists, the utility will copy the existing file into the new location, and continue processing remaining files.

_This could potentialy leave some files corrupted._

# Copyright
```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

Elements of `FoundationPlist.py` from `munki` are used in this tool.
https://github.com/munki/munki
