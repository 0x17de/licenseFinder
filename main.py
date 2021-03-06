#!/usr/bin/env python3

from sys import argv

from license_collector import LicenseCollector
from archive_provider import ArchiveProvider


GOOD='\033[92m'
NORMAL='\033[0m'
BOLD='\033[1m'
WARNING='\033[93m'
CRITICAL='\033[91m'


def check_match(filename, lc, buf):
    m = lc.match(filename, buf)
    if m is None:
        return
    sum = 0.0
    count = 0
    thename = None
    for match in m:
        if match is None:
            continue
        if thename is None:
            thename = match[1]
        count += 1
        sum += match[0]
        if thename != match[1]:
            thename = None
            break

    if thename is None:
        return

    color = CRITICAL
    ratio = sum / count
    if ratio > 0.97:
        color = GOOD
    elif ratio > 0.87:
        color = WARNING

    print("File: %s%s%s looks like '%s%s%s' (%s%.2f%%%s)" % (BOLD, filename, NORMAL, BOLD, thename, NORMAL, color, round(ratio * 100, 2), NORMAL))

def run():
    lc = LicenseCollector()

    printHelp = False
    aggressiveEnabled = False

    startIndex = 1

    for arg in argv[startIndex:]:
        if arg[0] == '-':
            startIndex += 1
            if arg[1] == 'a':
                aggressiveEnabled = True
            if arg[1] == 'h':
                printHelp = True
            if arg[1] == '-':
                if len(arg) > 2:
                    printHelp = True
                break
        else:
            break

    if printHelp:
        print("=== Help page ===")
        print("./{program} [options...] [files...]")
        print("-h   Prints this help")
        print("-a   Aggressive mode - Scan every text file.")
        print("--   Only files are following.")
        return

    args = argv[startIndex:]
    for arg in args:
        print("=== Scanning path \"{0}\" ===".format(arg))
        try:
            ap = ArchiveProvider(arg)
            for filename,buf in ap.get_candidates():
                check_match(filename, lc, buf)

            if aggressiveEnabled:
                print("--- Aggressive search ---")

                for filename,buf in ap.get_further_candidates():
                    check_match(filename, lc, buf)

        except FileNotFoundError as e:
            print("File not found: {0}".format(e.filename))

if __name__ == "__main__":
    run()
