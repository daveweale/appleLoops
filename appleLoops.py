#!/usr/bin/python

"""
Downloads required audio content for GarageBand and Logic Pro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Elements of FoundationPlist.py are used in this tool.

"""

import argparse
import collections
import os
import plistlib
import sys
import urllib2
from time import sleep

# PyLint cannot properly find names inside Cocoa libraries, so issues bogus
# No name 'Foo' in module 'Bar' warnings. Disable them.
# pylint: disable=E0611
from Foundation import NSData  # NOQA
from Foundation import NSPropertyListSerialization
from Foundation import NSPropertyListMutableContainers
from Foundation import NSPropertyListXMLFormat_v1_0  # NOQA
# pylint: enable=E0611


# Acknowledgements to Greg Neagle and `munki` for this section of code.
class FoundationPlistException(Exception):
    """Basic exception for plist errors"""
    pass


class NSPropertyListSerializationException(FoundationPlistException):
    """Read/parse error for plists"""
    pass


def readPlistFromString(data):
    '''Read a plist data from a string. Return the root object.'''
    try:
        plistData = buffer(data)
    except TypeError, err:
        raise NSPropertyListSerializationException(err)
    dataObject, dummy_plistFormat, error = (
        NSPropertyListSerialization.
        propertyListFromData_mutabilityOption_format_errorDescription_(
            plistData, NSPropertyListMutableContainers, None, None))
    if dataObject is None:
        if error:
            error = error.encode('ascii', 'ignore')
        else:
            error = "Unknown error"
        raise NSPropertyListSerializationException(error)
    else:
        return dataObject


class AppleLoops():
    def __init__(self, download_location=None):
        if not download_location:
            self.download_location = '/tmp'
        else:
            self.download_location = download_location

        # Base URL for loops
        # This URL needs to be re-assembled into the correct format of:
        # http://audiocontentdownload.apple.com/lp10_ms3_content_YYYY/filename.ext
        self.base_url = (
            'http://audiocontentdownload.apple.com/lp10_ms3_content_'
        )

        # Dictionary of plist feeds to parse
        # The dictionary contains two dictionaries, one for Logic Pro, the
        # other for GarageBand, which then contains a dictionary for release
        # year, which then has a list of plist feeds that Apple use for the
        # releases where loops are updated.
        # For example: self.loop_locations['logic_pro']['2016'][0]
        # Returns: 'logicpro1023.plist'
        self.logic_loop_locations = {
            '2016': [
                'logicpro1023.plist',
                'logicpro1022.plist',
            ],
            '2015': [
                'logicpro1020.plist',
                'logicpro1010.plist',  # Binary file
            ],
            '2013': [
                'logicpro1000_en.plist',
            ],
        }

        self.garageband_loop_locations = {
            '2016': [
                'garageband1012.plist',
                'garageband1011.plist',
            ],
            '2015': [
                'garageband1010.plist',
            ],
            '2013': [
                'garageband1000_en.plist',
            ],
        }

        self.premium_loops = {
            '2015': [
                'MAContent10_PremiumPreLoopsHipHop.pkg',
                'MAContent10_PremiumPreLoopsElectroHouse.pkg',
                'MAContent10_PremiumPreLoopsDubstep.pkg',
                'MAContent10_PremiumPreLoopsModernRnB.pkg',
                'MAContent10_PremiumPreLoopsTechHouse.pkg',
                'MAContent10_PremiumPreLoopsDeepHouse.pkg',
                'MAContent10_PremiumPreLoopsChillwave.pkg',
                'MAContent10_PremiumPreLoopsGarageBand.pkg',
                'MAContent10_PremiumPreLoopsJamPack1.pkg',
                'MAContent10_PremiumPreLoopsRemixTools.pkg',
                'MAContent10_PremiumPreLoopsRhythmSection.pkg',
                'MAContent10_PremiumPreLoopsSymphony.pkg',
                'MAContent10_PremiumPreLoopsWorld.pkg',
            ]
        }

        # Create a named tuple for our loops master list
        # These 'attributes' are:
        # pkg_name = Package file name
        # pkg_url = Package URL from Apple servers
        # pkg_mandatory = Required package for whatever app requires it
        # pkg_size = Package size based on it's 'Content-Length' - in bytes
        # pkg_year = The package release year (i.e. 2016, or 2013, etc)
        # pkg_loop_for = logicpro or garageband
        self.Loop = collections.namedtuple('Loop', ['pkg_name',
                                                    'pkg_url',
                                                    'pkg_mandatory',
                                                    'pkg_size',
                                                    'pkg_year',
                                                    'pkg_loop_for'])
        self.master_list = []
        self.duplicate_loops_list = []

    def build_url(self, loop_year, filename):
        seperator = '/'
        return seperator.join([self.base_url + loop_year, filename])

    def add_loop(self, package_name, package_url,
                 package_mandatory, package_size, package_year, loop_for):
        loop = self.Loop(
            pkg_name=package_name,
            pkg_url=package_url,
            pkg_mandatory=package_mandatory,
            pkg_size=package_size,
            pkg_year=package_year,
            pkg_loop_for=loop_for
        )
        if loop not in self.master_list:
            self.master_list.append(loop)
        else:
            if loop not in self.duplicate_loops_list:
                self.duplicate_loops_list.append(loop)

    def process_plist(self, loop_year, plist):
        # Note - the package size specified in the plist feeds doesn't always
        # match the actual package size, so check header 'Content-Length' to
        # determine correct package size.
        plist_url = self.build_url(loop_year, plist)
        request = urllib2.urlopen(plist_url)
        data = readPlistFromString(request.read())
        loop_for = os.path.splitext(plist)[0]
        loop_for = ''.join(map(lambda c: '' if c in '0123456789' else c,
                               loop_for))

        for pkg in data['Packages']:
            name = data['Packages'][pkg]['DownloadName']
            url = self.build_url(loop_year, name)

            # The 'IsMandatory' may not exist, if it doesn't, then the package
            # isn't mandatory, duh.
            try:
                mandatory = data['Packages'][pkg]['IsMandatory']
            except:
                mandatory = False

            # If the package download name starts with ../ then we need to fix
            # the URL up to point to the right path, and adjust the pkg name
            # Additionally, replace the year with the correct year
            if name.startswith('../'):
                url = 'http://audiocontentdownload.apple.com/%s' % name[3:]
                name = os.path.basename(name)

            # List comprehension to get the year
            year = [x[-4:] for x in url.split('/') if 'lp10_ms3' in x][0]

            size_request = urllib2.urlopen(url)
            size = size_request.info().getheader('Content-Length').strip()
            size_request.close()

            # Add to the loops master list
            self.add_loop(name, url, mandatory, size, year, loop_for)

        # Tidy up the urllib2 request
        request.close()

    def build_loops_master_list(self):
        for year in self.logic_loop_locations:
            for plist in self.logic_loop_locations[year]:
                self.process_plist(year, plist)

        for year in self.garageband_loop_locations:
            for plist in self.garageband_loop_locations[year]:
                self.process_plist(year, plist)


loops = AppleLoops()

# loops.process_plist('2016', 'logicpro1023.plist')
loops.build_loops_master_list()

print len(loops.duplicate_loops_list)
print len(loops.master_list)
