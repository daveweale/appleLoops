# appleLoops.py

## What does it do?
This utility can download all the essential content required by GarageBand, Logic Pro X, and MainStage, as well as optional content that is available for the same apps.

**You are responsible for being appropriately licensed for any/all content downloaded with this tool.**

## What this won't do
* Install packages
* Import packages into your package deployment system
* Download content for older versions of GarageBand, Logic Pro X, and MainStage.

## Requirements
macOS with the system standard `python` and an active Internet connection.

## GarageBand first run behaviour
The current version of GarageBand (10.1.5 as at 2017-01-19) does the following:
- Downloads 33 'essential' packages (~1.87GB) for basic functionality
- Prompts to download 359 optional packages (~26.49GB) for extended functionality

## Logic Pro X first run behaviour
The current version of Logic Pro X (10.3.0 as at 2017-01-19):
- Requires 33 packages of 'essential' content (~1.96GB) for basic functionality
- Has 567 optional packages (~43.73GB)

## MainStage 3 first run behaviour
The current version of MainStage 3 (3.2.4 as at 2016-11-23):
- Requires 35 packages of 'essential' content (~1.68GB) for basic functionality
- Has 547 optional packages (~43.31GB)

### Common Content
All three apps do have a number of packages that are shared in common, both in the essential package sets, and optional package sets.

## Usage
* `git clone https://github.com/jcitizen/appleLoops`
* `./appleLoops.py --help` for usage

### Quick usage examples
* `./appleLoops.py --help` show all options
* `./appleLoops.py` will download all GarageBand content (optional and mandatory)
* `./appleLoops.py --dry-run --package-set garageband --optional-only` will do a dry run for all GarageBand optional content
* `./appleLoops.py --package-set garageband--mandatory-only` will download all essential GarageBand content
* `./appleLoops.py --package-set logicpro --mandatory-only` will download all essential Logic Pro X content
* `./appleLoops.py --package-set mainstage --cache-server http://cache_server:port --destination ~/Desktop/loops` will download all MainStage content through the specified caching server, and store packages in the `~/Desktop/loops` folder.
* `/.appleLoops.py --file garageband1012.plist` will download all packages found in the `garageband1012.plist` file bundled with several versions of GarageBand.

## Behaviour

### Proxies
Untested - if there are issues with using this to download the content whilst behind a proxy, try downloading outside of the content, or if you can contribute some code to improve that behaviour, please feel free to create a pull request.

### Package download location
Packages will be saved into the `/tmp/appleLoops` folder by default, unless the `-d, --destination <folder>` flag and argument is provided.

To ensure that content is readily identifiable, it is stored in a folder within the `/tmp/appleLoops` depending on the plist file it was processed from, year, and whether it was mandatory or not.

#### Example for GarageBand content:
```
[jcitizen@computer]:mandatory # pwd
/tmp/appleLoops/garageband1012/2016/mandatory
[jcitizen@computer]:mandatory # ls -lha
total 4118408
drwxr-xr-x  37 jcitizen  wheel   1.2K  3 Feb 18:19 .
drwxr-xr-x   4 jcitizen  wheel   136B  3 Feb 17:55 ..
-rw-r--r--   1 jcitizen  wheel    11M  3 Feb 18:15 MAContent10_AssetPack_0048_AlchemyPadsDigitalHolyGhost.pkg
-rw-r--r--   1 jcitizen  wheel    19M  3 Feb 18:18 MAContent10_AssetPack_0310_UB_DrumMachineDesignerGB.pkg
-rw-r--r--   1 jcitizen  wheel    26M  3 Feb 18:19 MAContent10_AssetPack_0312_UB_UltrabeatKitsGBLogic.pkg
-rw-r--r--   1 jcitizen  wheel   153M  3 Feb 18:06 MAContent10_AssetPack_0314_AppleLoopsHipHop1.pkg
-rw-r--r--   1 jcitizen  wheel    40M  3 Feb 17:57 MAContent10_AssetPack_0315_AppleLoopsElectroHouse1.pkg
-rw-r--r--   1 jcitizen  wheel   7.1M  3 Feb 18:01 MAContent10_AssetPack_0316_AppleLoopsDubstep1.pkg
-rw-r--r--   1 jcitizen  wheel    17M  3 Feb 18:06 MAContent10_AssetPack_0317_AppleLoopsModernRnB1.pkg
-rw-r--r--   1 jcitizen  wheel    36M  3 Feb 18:15 MAContent10_AssetPack_0320_AppleLoopsChillwave1.pkg
-rw-r--r--   1 jcitizen  wheel    16M  3 Feb 18:08 MAContent10_AssetPack_0321_AppleLoopsIndieDisco.pkg
-rw-r--r--   1 jcitizen  wheel    16M  3 Feb 17:56 MAContent10_AssetPack_0322_AppleLoopsDiscoFunk1.pkg
-rw-r--r--   1 jcitizen  wheel    33M  3 Feb 18:16 MAContent10_AssetPack_0323_AppleLoopsVintageBreaks.pkg
-rw-r--r--   1 jcitizen  wheel    31M  3 Feb 18:14 MAContent10_AssetPack_0324_AppleLoopsBluesGarage.pkg
-rw-r--r--   1 jcitizen  wheel    21M  3 Feb 18:16 MAContent10_AssetPack_0325_AppleLoopsGarageBand1.pkg
-rw-r--r--   1 jcitizen  wheel   139M  3 Feb 18:11 MAContent10_AssetPack_0354_EXS_PianoSteinway.pkg
-rw-r--r--   1 jcitizen  wheel    16M  3 Feb 17:57 MAContent10_AssetPack_0357_EXS_BassAcousticUprightJazz.pkg
-rw-r--r--   1 jcitizen  wheel    35M  3 Feb 18:19 MAContent10_AssetPack_0358_EXS_BassElectricFingerStyle.pkg
-rw-r--r--   1 jcitizen  wheel    29M  3 Feb 17:56 MAContent10_AssetPack_0371_EXS_GuitarsAcoustic.pkg
-rw-r--r--   1 jcitizen  wheel    30M  3 Feb 18:19 MAContent10_AssetPack_0375_EXS_GuitarsVintageStrat.pkg
-rw-r--r--   1 jcitizen  wheel    22M  3 Feb 18:16 MAContent10_AssetPack_0482_EXS_OrchWoodwindAltoSax.pkg
-rw-r--r--   1 jcitizen  wheel    28M  3 Feb 18:00 MAContent10_AssetPack_0484_EXS_OrchWoodwindClarinetSolo.pkg
-rw-r--r--   1 jcitizen  wheel    26M  3 Feb 17:56 MAContent10_AssetPack_0487_EXS_OrchWoodwindFluteSolo.pkg
-rw-r--r--   1 jcitizen  wheel   186M  3 Feb 18:04 MAContent10_AssetPack_0491_EXS_OrchBrass.pkg
-rw-r--r--   1 jcitizen  wheel    48M  3 Feb 18:06 MAContent10_AssetPack_0509_EXS_StringsEnsemble.pkg
-rw-r--r--   1 jcitizen  wheel    18M  3 Feb 18:16 MAContent10_AssetPack_0536_DrummerClapsCowbell.pkg
-rw-r--r--   1 jcitizen  wheel    11M  3 Feb 17:56 MAContent10_AssetPack_0537_DrummerShaker.pkg
-rw-r--r--   1 jcitizen  wheel   804K  3 Feb 17:56 MAContent10_AssetPack_0538_DrummerSticks.pkg
-rw-r--r--   1 jcitizen  wheel    20M  3 Feb 18:06 MAContent10_AssetPack_0539_DrummerTambourine.pkg
-rw-r--r--   1 jcitizen  wheel   108K  3 Feb 17:56 MAContent10_AssetPack_0540_PlugInSettingsGB.pkg
-rw-r--r--   1 jcitizen  wheel   312K  3 Feb 17:56 MAContent10_AssetPack_0541_PlugInSettingsGBLogic.pkg
-rw-r--r--   1 jcitizen  wheel    20M  3 Feb 18:10 MAContent10_AssetPack_0554_AppleLoopsDiscoFunk2.pkg
-rw-r--r--   1 jcitizen  wheel   217M  3 Feb 17:58 MAContent10_AssetPack_0560_LTPBasicPiano1.pkg
-rw-r--r--   1 jcitizen  wheel   241M  3 Feb 18:03 MAContent10_AssetPack_0593_DrummerSoCalGBLogic.pkg
-rw-r--r--   1 jcitizen  wheel    15M  3 Feb 17:56 MAContent10_AssetPack_0597_LTPChordTrainer.pkg
-rw-r--r--   1 jcitizen  wheel   275M  3 Feb 18:09 MAContent10_AssetPack_0598_LTPBasicGuitar1.pkg
-rw-r--r--   1 jcitizen  wheel   212M  3 Feb 18:01 MAContent10_AssetPack_0599_GBLogicAlchemyEssentials.pkg
[jcitizen@computer]:mandatory #
```

### Duplicate content
Where a package from one app is used in another app, if a local copy already exists in other folders, copy that into the new location instead of downloading it again.

This only checks the default `/tmp/appleLoops` path or the specified path supplied with the `-d` or `--destination-path` arguments.

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
