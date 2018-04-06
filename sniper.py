#!/usr/bin/python
######################################################################
#
# File: sniper.py
#
# Description:  A small script that is similar to killnow,
#               but with added features.
#
# (c) Copyright 2018 Adam W. Dace.  All rights reserved.
#
######################################################################

# Pydoc comments
"""Application entry point. """

# File version tag
__version__ = '1.2'

# Standard modules
import commands
import getopt
import sys

######################################################################
# Good old main...
######################################################################

def main(argv):
    """Good old main."""

    usage = """Usage: %s [OPTION] SEARCHSTRING

This script attempts to locate a given process(or processes) within the
process table on a given server.  Unlike killall and its relatives,
it is extremely verbose and offers a test mode so one can see what results
a given command will produce before running it.

The available options are:

    -h / --help
    Prints this usage statement.
    OPTIONAL

    -s=SIGNAL / --signal=SIGNAL
    Specifies the signal we wish to send selected processes.
    Default: SIGKILL
    OPTIONAL

    -t / --test
    Specifies we wish to know what the script would do,
    instead of actually performing them.
    Default: False
    OPTIONAL

    --version
    Prints the version banner.
    OPTIONAL

Exit Status Codes:
------------------
0 = Success
1 = No matching processes found.
2 = Other exception caught and script aborted.

Examples:
---------
sniper.py --signal SIGTERM --test EVILPROC
sniper.py EVILPROC
""" % argv[0]

    version = """sinper.py v%s
Sniper.  Processes check in.  They don't check out.
(c) Copyright 2018 Adam W. Dace  All rights reserved.
-----------------------------------------------------""" % __version__

######################################################################
# Variable initialization.
######################################################################

    # Various variables.
    search_pattern = ''
    seperator = '---------------------------------------------------------------------------'
    signal='SIGKILL'
    is_test_mode=False

    # Getopt variables.
    short_options = 'hs:tv?'
    long_options = ['help',
                    'signal=',
                    'test',
                    'version',
                    '?']

######################################################################
# Main logic flow.
######################################################################

    try:
        optlist, args = \
                 getopt.getopt(sys.argv[1:], short_options, long_options)

        if len(optlist) > 0:
            for opt in optlist:
                if (opt[0] in ('-s', '--signal')):
                    signal=opt[1]
                elif (opt[0] in ('-h', '-?', '--help', '--?')):
                    print(version)
                    print(usage)
                    sys.exit(0)
                elif (opt[0] in ('-t', '--test')):
                    is_test_mode=1
                elif (opt[0] in ('-v', '--version')):
                    print(version)
                    sys.exit(0)

        if len(args) > 0:
            search_pattern = args[0]
        else:
            raise RuntimeError

    except RuntimeError:
        print(version)
        print("ERROR: Invalid argument or flag found.  Please check your syntax.")
        print("ERROR: Please run again with the --help flag for more information.")
        print
        sys.exit(1)

    except getopt.GetoptError:
        print(version)
        print("ERROR: Invalid argument or flag found.  Please check your syntax.")
        print("ERROR: Please run again with the --help flag for more information.")
        sys.exit(1)

    # Validate the signal we're sending actually exists.
    status, output = commands.getstatusoutput("kill -l | grep " + signal)

    if len(output) == 0:
        print("ERROR: No matching signal found for string '" + signal + "'.  Perhaps a typo?  Exiting...")
        sys.exit(1)

    # The hunt begins!
    status, output = commands.getstatusoutput("ps -ef | grep " + search_pattern + " | grep -v grep | grep -v sniper.py")

    if status != 0:
        print("ERROR: No matching processes found for string '" + search_pattern + "'.  Exiting...") 
        sys.exit(1)

    print("INFO:  Found at least one matching process, 'ps -ef' output follows...")
    print("INFO:  " + seperator)
    for line in output.split('\n'):
        print("INFO:  " + line)
    print("INFO:  " + seperator)

    # Gather target PID list.
    status, output = commands.getstatusoutput("ps -ef | grep " + search_pattern + " | grep -v grep | grep -v sniper.py | awk ' { print $2 } ' | xargs echo")

    if status != 0:
        print("ERROR: Caught non-zero exit code from 'ps -ef'.  This shouldn't be possible!  Exiting...")
        sys.exit(2)

    kill_command = "kill -s " + signal + " " + output

    print("INFO:  Target Signal: |" + signal + "|") 
    print("INFO:  Target PIDs:   |" + output + "|")
    print("INFO:  Kill Cmd:      |" + kill_command + "|")
    print("INFO:  " + seperator)

    if (is_test_mode):
        print("INFO:  Test mode confirmed.  Taking no real action, exiting...")
    else:
        print("INFO:  Sniper mode confirmed.  Sending signals...")

        # Exterminate!
        status, output = commands.getstatusoutput(kill_command)

        print

        if status != 0:
            print("ERROR: Caught non-zero exit code kill command.  Output follows...")
            print("ERROR: " + seperator)
            for line in output.split('\n'):
                print("ERROR: " + line)
            print("ERROR: " + seperator)

            sys.exit(2)

        print("INFO:  Kill command returned success exit code.  Work completed.")

######################################################################
# If called from the command line, invoke thyself!
######################################################################

if __name__=='__main__': main(sys.argv)

######################################################################
