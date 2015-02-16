#!/usr/bin/env python3

from sys import argv

from license_collector import LicenseCollector
from archive_provider import ArchiveProvider


def run():
    lc = LicenseCollector()

    args = argv[1:]
    for arg in args:
        print("=== Scanning path \"{0}\" ===".format(arg))
        try:
            with ArchiveProvider(arg) as ap:
                for name,buf in ap.get_candidates():
                    m = lc.match(name,buf)
                    if m is None:
                        print("Could not match candidate: {0}".format(name))
                    else:
                        print("File: {0} looks like {1}".format(name,m))

                print("--- Aggressive search ---")

                for name,buf in ap.get_further_candidates():
                    m = lc.match(name,buf)
                    if not m is None:
                        print("File: {0} looks like {1}".format(name,m))
        except FileNotFoundError as e:
            print("File not found: {0}".format(e.filename))

if __name__ == "__main__":
    run()
