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
https://github.com/munki/munki
"""

import argparse
import collections
import os
import sys
import urllib2
from random import uniform
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
    def __init__(self, download_location=None, dry_run=True,
                 mandatory_pkgs=False, package_set=None,
                 package_year=None):
        if not download_location:
            self.download_location = os.path.join('/tmp', 'appleLoops')
        else:
            self.download_location = download_location

        # Default to dry run
        self.dry_run = dry_run

        # Set mandatory packages or not, defaults to false
        self.mandatory_packages = mandatory_pkgs

        # Set package set to download
        self.package_set = package_set

        # Set package year to download
        self.package_year = package_year

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
        # Note - dropped support for anything prior to 2016 releases
        self.logic_loop_locations = {
            '2016': [
                'logicpro1023.plist',
            ],
        }

        self.garageband_loop_locations = {
            '2016': [
                'garageband1012.plist',
            ],
        }

        self.loop_years = ['2016']
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

    def process_plist(self, loop_year, plist):
        # Note - the package size specified in the plist feeds doesn't always
        # match the actual package size, so check header 'Content-Length' to
        # determine correct package size.
        plist_url = self.build_url(loop_year, plist)
        request = urllib2.urlopen(plist_url)
        data = readPlistFromString(request.read())
        loop_for = os.path.splitext(plist)[0]

        # I don't like using regex, so here's a lambda to remove numbers from
        # part of the loop URL to use as an indicator for what app the loops is
        # for
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

            # This step adds time to the processing of the plist
            try:
                size_request = urllib2.urlopen(url)
                size = size_request.info().getheader('Content-Length').strip()
                # Close out the urllib2 request
                size_request.close()
            except:
                size = data['Packages'][pkg]['DownloadSize']

            # Add to the loops master list
            self.add_loop(name, url, mandatory, size, year, loop_for)

        # Tidy up the urllib2 request
        request.close()

    def build_master_list(self, loops_for=None):
        if 'logicpro' in loops_for:
            self.process_plist('2016', 'logicpro1023.plist')
        #    for year in self.logic_loop_locations:
        #        for plist in self.logic_loop_locations[year]:
        #            self.process_plist(year, plist)

        if 'garageband' in loops_for:
            self.process_plist('2016', 'garageband1012.plist')
        #    for year in self.garageband_loop_locations:
        #        for plist in self.garageband_loop_locations[year]:
        #            self.process_plist(year, plist)

    def convert_size(self, file_size, precision=2):
        try:
            suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
            suffix_index = 0
            while file_size > 1024 and suffix_index < 4:
                suffix_index += 1
                file_size = file_size/1024.0

            return '%.*f%s' % (precision, file_size, suffixes[suffix_index])
        except Exception as e:
            raise e

    def progress_output(self, loop, percent, human_fs):
        try:
            stats = 'Downloading: %s' % (loop.pkg_name)
            progress = '[%0.2f%% of %s]' % (percent, human_fs)
            sys.stdout.write("\r%s %s" % (stats, progress))
            sys.stdout.flush()
        except Exception as e:
            raise e

    def make_storage_location(self, folder):
        try:
            folder = os.path.expanduser(folder)
        except:
            pass

        try:
            folder = os.path.expandvar(folder)
        except:
            pass

        if not os.path.isdir(folder):
            try:
                os.makedirs(folder)
            except Exception as e:
                raise e

    def download(self, loop):
        local_directory = os.path.join(self.download_location,
                                       loop.pkg_loop_for,
                                       loop.pkg_year)
        self.make_storage_location(local_directory)
        if not self.dry_run:
            # return 'Not a dry run'
            try:
                request = urllib2.urlopen(loop.pkg_url)

                # Human readable file size
                loop_size = self.convert_size(float(loop.pkg_size))
            except Exception as e:
                raise e
            else:
                # Open a local file to write into in binary format
                local_file = open(os.path.join(local_directory, loop.pkg_name),
                                  'wb')
                bytes_so_far = 0

                # This bit does the download
                while True:
                    buffer = request.read(8192)
                    if not buffer:
                        print('')
                        break

                    # Re-calculate downloaded bytes
                    bytes_so_far += len(buffer)

                    # Write out download file to the loop_file opened
                    local_file.write(buffer)

                    # Calculate percentage
                    percent = float(bytes_so_far) / int(loop.pkg_size)
                    percent = round(percent*100, 2)

                    # Output progress made
                    self.progress_output(loop, percent, loop_size)
            finally:
                try:
                    request.close()
                except:
                    pass
                else:
                    # Let a random sleep of 1-5 seconds happen between each
                    # download
                    pause = uniform(1, 5)
                    sleep(pause)

        else:
            print 'Dry run'

    # This is the primary processor for the main function - only used for
    # command line based script usage
    def main_processor(self):
        pkg_set = self.package_set

        for pkg in pkg_set:
            for loop in self.master_list:
                if loop.year in self.package_year:
                    self.download(loop)


def main():
    class SaneUsageFormat(argparse.HelpFormatter):
        """
            for matt wilkie on SO
            http://stackoverflow.com/questions/9642692/argparse-help-without-duplicate-allcaps/9643162#9643162
        """
        def _format_action_invocation(self, action):
            if not action.option_strings:
                default = self._get_default_metavar_for_positional(action)
                metavar, = self._metavar_formatter(action, default)(1)
                return metavar

            else:
                parts = []

                # if the Optional doesn't take a value, format is:
                #    -s, --long
                if action.nargs == 0:
                    parts.extend(action.option_strings)

                # if the Optional takes a value, format is:
                #    -s ARGS, --long ARGS
                else:
                    default = self._get_default_metavar_for_optional(action)
                    args_string = self._format_args(action, default)
                    for option_string in action.option_strings:
                        parts.append(option_string)

                    return '%s %s' % (', '.join(parts), args_string)

                return ', '.join(parts)

        def _get_default_metavar_for_optional(self, action):
            return action.dest.upper()

    parser = argparse.ArgumentParser(formatter_class=SaneUsageFormat)

    # Option for package set (either 'garageband' or 'logicpro')
    parser.add_argument(
        '-p', '--package-set',
        type=str,
        nargs='+',
        dest='package_set',
        choices=['garageband', 'logicpro'],
        help='Specify one or more package set to download',
        required=False
    )

    # Option for dry run
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        dest='dry_run',
        help='Dry run to indicate what will be downloaded',
        required=False
    )

    # Option for mandatory packages only
    parser.add_argument(
        '-m', '--mandatory-only',
        action='store_true',
        dest='mandatory_only',
        help='Download mandatory packages only',
        required=False
    )

    # Option for output directory
    parser.add_argument(
        '-o', '--output',
        type=str,
        nargs=1,
        dest='output',
        metavar='<folder>',
        help='Download location for loops content',
        required=False
    )

    # Option for content year
    parser.add_argument(
        '-y', '--content-year',
        type=str,
        nargs='+',
        dest='content_year',
        choices=AppleLoops().loop_years,
        help='Specify one or more content year to download',
        required=False
    )

    args = parser.parse_args()

    # Set which package set to download
    if args.package_set:
        pkg_set = args.package_set
    else:
        pkg_set = ['garageband']

    # Set output directory
    if args.output and len(args.output) is 1:
        store_in = args.output[0]
    else:
        store_in = None

    # Set mandatory packages option for when class is instantiated
    if not args.mandatory_only:
        mandatory = False
    else:
        mandatory = True

    # Set content year
    if not args.content_year:
        year = ['2016']
    else:
        year = args.content_year

    # Instantiate the class AppleLoops with options
    loops = AppleLoops(download_location=store_in,
                       dry_run=args.dry_run,
                       mandatory_pkgs=mandatory,
                       package_set=pkg_set,
                       package_year=year)

    # loops.main_processor()
    print args

if __name__ == '__main__':
    main()
