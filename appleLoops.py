#!/usr/bin/python

"""
Downloads required audio loops for GarageBand, Logic Pro X, and MainStage 3.

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

# Script information
__author__ = 'Carl Windus'
__copyright__ = 'Copyright 2016, Carl Windus'
__credits__ = ['Greg Neagle', 'Matt Wilkie']
__version__ = '1.0.0'
__date__ = '2016-12-23'

__license__ = 'Apache License, Version 2.0'
__maintainer__ = 'Carl Windus'
__status__ = 'Production'


# Acknowledgements to Greg Neagle and `munki` for this section of code.
class FoundationPlistException(Exception):
    """Basic exception for plist errors"""
    pass


class NSPropertyListSerializationException(FoundationPlistException):
    """Read/parse error for plists"""
    pass


def readPlistFromString(data):
    """Read a plist data from a string. Return the root object."""
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
    """Class contains functions for parsing Apple's plist feeds for GarageBand
    and Logic Pro, as well as downloading loops content."""
    def __init__(self, download_location=None, dry_run=True,
                 package_set=None, package_year=None,
                 mandatory_pkg=False, optional_pkg=False):
        if not download_location:
            self.download_location = os.path.join('/tmp', 'appleLoops')
        else:
            self.download_location = download_location

        # Default to dry run
        self.dry_run = dry_run

        # Set package set to download
        self.package_set = package_set

        # Set package year to download
        self.package_year = package_year

        # Set mandatory package to option specified. Default is false.
        self.mandatory_pkg = mandatory_pkg

        # Set optional package to option specified. Default is false.
        self.optional_pkg = optional_pkg

        # User-Agent string for this tool
        self.user_agent = 'appleLoops/%s' % __version__

        # Base URL for loops
        # This URL needs to be re-assembled into the correct format of:
        # http://audiocontentdownload.apple.com/lp10_ms3_content_YYYY/filename.ext
        self.base_url = (
            'http://audiocontentdownload.apple.com/lp10_ms3_content_'
        )

        # Dictionary of plist feeds to parse - these are Apple provided plists
        # Will look into possibly using local copies maintained in
        # GarageBand/Logic Pro X app bundles.
        # Note - dropped support for anything prior to 2016 releases
        self.feeds = self.request_url('https://raw.githubusercontent.com/carlashley/appleLoops/test/com.github.carlashley.appleLoops.feeds.plist')  # NOQA
        self.loop_feed_locations = readPlistFromString(self.feeds.read())
        self.feeds.close()

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

        # Empty list to put all the content that we're going to work on into.
        self.master_list = []

        # Download amount list
        self.download_amount = []

    def build_url(self, loop_year, filename):
        """Builds the URL for each plist feed"""
        seperator = '/'
        return seperator.join([self.base_url + loop_year, filename])

    # Wrap around urllib2 for requesting URL's because this is done often
    # enough
    def request_url(self, url):
        req = urllib2.Request(url)
        req.add_unredirected_header('User-Agent', self.user_agent)
        req = urllib2.urlopen(req)
        return req

    def add_loop(self, package_name, package_url,
                 package_mandatory, package_size, package_year, loop_for):
        """Add's the loop to the master list. A named tuple is used to make
        referencing attributes of each loop easier."""
        # Apple aren't consistent with file sizes - so if the file size comes
        # from the plist, we may need to remove characters!
        try:
            package_size = package_size.replace('.', '')
        except:
            pass

        # Use the tuple Luke!
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
        """Processes the Apple plist feed. Makes use of readPlistFromString()
        as python's native plistlib module doesn't read binary plists, which
        Apple has used in past releases."""
        # Note - the package size specified in the plist feeds doesn't always
        # match the actual package size, so check header 'Content-Length' to
        # determine correct package size.
        plist_url = self.build_url(loop_year, plist)

        # URL requests
        request = self.request_url(plist_url)

        # Process request data into dictionary
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
                request = self.request_url(url)
                size = request.info().getheader('Content-Length').strip()

                # Close out the urllib2 request
                request.close()
            except:
                size = data['Packages'][pkg]['DownloadSize']

            # Add to the loops master list
            if self.mandatory_pkg and not self.optional_pkg:
                if mandatory:
                    self.add_loop(name, url, mandatory, size, year, loop_for)
            elif self.optional_pkg and not self.mandatory_pkg:
                if not mandatory:
                    self.add_loop(name, url, mandatory, size, year, loop_for)
            else:
                pass

            if not self.mandatory_pkg and not self.optional_pkg:
                self.add_loop(name, url, mandatory, size, year, loop_for)

        # Tidy up the urllib2 request
        request.close()

    def build_master_list(self):
        """This builds the master list of audio content so it (the master list)
        can be processed in other functions. Yeah, there's some funky Big O
        here."""
        # Yo dawg, heard you like for loops, so I put for loops in your for
        # loops
        for pkg_set in self.package_set:
            for year in self.package_year:
                package_plist = self.loop_feed_locations[pkg_set][year]
                for plist in package_plist:
                    print 'Processing items from %s and saving to %s' % (
                        plist, self.download_location
                    )
                    self.process_plist(year, plist)

    def convert_size(self, file_size, precision=2):
        """Converts the package file size into a human readable number."""
        try:
            suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
            suffix_index = 0
            while file_size > 1024 and suffix_index < 4:
                suffix_index += 1
                file_size = file_size/1024.0

            return '%.*f%s' % (precision, file_size, suffixes[suffix_index])
        except Exception as e:
            raise e

    def progress_output(self, loop, percent, human_fs, items_counter):
        """Basic progress count that self updates while a
        file is downloading."""
        try:
            stats = 'Downloading %s: %s' % (items_counter, loop.pkg_name)
            progress = '[%0.2f%% of %s]' % (percent, human_fs)
            sys.stdout.write("\r%s %s" % (stats, progress))
            sys.stdout.flush()
        except Exception as e:
            raise e

    def make_storage_location(self, folder):
        """Makes the storage location for the audio content if it doesn't exist.
        Tries to expand paths and variables."""
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

    # Test if the file being downloaded exists
    def file_exists(self, loop, local_file):
        """Tests if the remote file already exists locally and it is the
        correct file size. There is potential for some file size discrepancy
        based on how many blocks the file actually takes up on local storage.
        So some files may end up being re-downloaded as a result.
        To get around this, calculate the number of blocks the local file
        consumes, and compare that to the number of blocks the remote file
        would consume."""
        if os.path.exists(local_file):
            # Get the block size of the file on disk
            block_size = os.stat(local_file).st_blksize

            # Remote file size
            remote_blocks = int(int(loop.pkg_size)/block_size)

            # Local file size
            local_blocks = int(os.path.getsize(local_file)/block_size)

            # Compare if local number of blocks consumed is equal to or greater
            # than the number of blocks the remote file will consume.
            if local_blocks >= remote_blocks:
                return True
            else:
                return False

    # Downloads the loop file
    def download(self, loop, counter):
        """Downloads the loop, if the dry run option has been set, then it will
        only output what it would download, along with the file size."""
        if loop.pkg_mandatory:
            local_directory = os.path.join(self.download_location,
                                           loop.pkg_loop_for,
                                           loop.pkg_year,
                                           'mandatory')

        if not loop.pkg_mandatory:
            local_directory = os.path.join(self.download_location,
                                           loop.pkg_loop_for,
                                           loop.pkg_year,
                                           'optional')

        local_file = os.path.join(local_directory, loop.pkg_name)

        # Do the download if this isn't a dry run
        if not self.dry_run:
            # Only create the output directory if this isn't a dry run
            # Make the download directory
            self.make_storage_location(local_directory)

            # If the file doesn't already exist, or isn't a complete file,
            # download it
            if not self.file_exists(loop, local_file):
                try:
                    request = self.request_url(loop.pkg_url)
                except Exception as e:
                    raise e
                else:
                    # Open a local file to write into in binary format
                    local_file = open(local_file, 'wb')
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
                        # local_file.flush()
                        os.fsync(local_file)

                        # Calculate percentage
                        percent = (
                            float(bytes_so_far) / float(loop.pkg_size)
                        )
                        percent = round(percent*100.0, 2)

                        # Some files take up more space locally than
                        # remote, so if percentage exceeds 100%, cap it.
                        if percent >= 100.0:
                            percent = 100.0

                        # Output progress made
                        items_count = '%s of %s' % (counter,
                                                    len(self.master_list))
                        self.progress_output(loop, percent,
                                             self.convert_size(float(
                                                 loop.pkg_size)),
                                             items_count)
                finally:
                    try:
                        request.close()
                        self.download_amount.append(float(loop.pkg_size))
                    except:
                        pass
                    else:
                        # Let a random sleep of 1-5 seconds happen between
                        # each download
                        pause = uniform(1, 5)
                        sleep(pause)
            else:
                print 'Skipped %s of %s: %s - file exists' % (
                    counter, len(self.master_list), loop.pkg_name
                )
        else:
            print 'Download: %s - %s' % (
                loop.pkg_name, self.convert_size(float(loop.pkg_size))
            )
            self.download_amount.append(float(loop.pkg_size))

    # This is the primary processor for the main function - only used for
    # command line based script usage
    def main_processor(self):
        """This is the main processor function, it should only be called in the
        main() function - i.e. only for use by the command line."""
        # Build master list
        self.build_master_list()

        # Do the download, and supply counter for feedback on progress
        counter = 1
        for loop in self.master_list:
            self.download(loop, counter)
            counter += 1

        # Additional information for end of download run
        download_amount = sum(self.download_amount)

        if self.dry_run:
            print '%s packages to download: %s' % (
                len(self.master_list), self.convert_size(download_amount)
            )
        else:
            if len(self.download_amount) >= 1:
                print 'Downloaded: %s ' % self.convert_size(download_amount)


def main():
    class SaneUsageFormat(argparse.HelpFormatter):
        """
        Makes the help output somewhat more sane.
        Code used was from Matt Wilkie.
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
    exclusive_group = parser.add_mutually_exclusive_group()

    # Option for package set (either 'garageband' or 'logicpro')
    parser.add_argument(
        '-p', '--package-set',
        type=str,
        nargs='+',
        dest='package_set',
        choices=['garageband', 'logicpro', 'mainstage'],
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

    # Option for mandatory content only
    exclusive_group.add_argument(
        '-m', '--mandatory-only',
        action='store_true',
        dest='mandatory',
        help='Download mandatory content only',
        required=False
    )

    # Option for optional content only
    exclusive_group.add_argument(
        '-o', '--optional-only',
        action='store_true',
        dest='optional',
        help='Download optional content only',
        required=False
    )

    # Option for output directory
    parser.add_argument(
        '-d', '--destination',
        type=str,
        nargs=1,
        dest='destination',
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
    if args.destination and len(args.destination) is 1:
        store_in = args.destination[0]
    else:
        store_in = None

    # Set content year
    if not args.content_year:
        year = ['2016']
    else:
        year = args.content_year

    # Instantiate the class AppleLoops with options
    loops = AppleLoops(download_location=store_in,
                       dry_run=args.dry_run,
                       package_set=pkg_set,
                       package_year=year,
                       mandatory_pkg=args.mandatory,
                       optional_pkg=args.optional)

    loops.main_processor()

if __name__ == '__main__':
    main()
