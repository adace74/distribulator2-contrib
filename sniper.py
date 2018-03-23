#!/usr/bin/python
######################################################################
#
# File: sniper.py
#
# Description:  Small script that will, via shell commands,
# search the process table and kill targets accordingly.
#
# Copyright (c) 2018, Adam W. Dace.  All Rights Reserved.
# Please see the accompanying LICENSE file for license information.
#
######################################################################

# Pydoc comments
"""Application entry point. """

# File version tag
__version__ = '1.2.0'

# Standard modules
import commands
import exceptions
import getopt
import sys

######################################################################
# Good old main...
######################################################################

def main(argv):
    """Good old main."""

    short_options = ['']
    long_options = ['help',
                    'test',
                    'signal=',
                    'version',
                    '?']

    usage = """Usage: %s [OPTION] SEARCHSTRING

This script attempts to locate a given process(or processes) within the
process table on a given server.  Unlike killall and its relatives,
it is extremely verbose and offers a test mode so one can see what results
a given command will produce before running it.

The available options are:

    --help
    Prints this usage statement.
    OPTIONAL

    --signal=SIGNAL
    Specifies the signal we wish to send selected processes.
    Default: SIGKILL
    OPTIONAL

    --test
    Specifies we wish to know the results of our actions, instead of actually performing them.
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
Copyright (c) 2018, Adam W. Dace.  All Rights Reserved.
-----------------------------------------------------""" % __version__

######################################################################
# Variable initialization.
######################################################################

    _SearchPattern=''
    _Seperator='--------------------------------------------------------------------------------'
    _Signal='SIGKILL'
    _TestMode=0

######################################################################
# Main logic flow.
######################################################################

    try:
        optlist, args = \
                 getopt.getopt(sys.argv[1:], short_options, long_options)

        if len(optlist) > 0:
            for opt in optlist:
                if (opt[0] == '--signal'):
                    _Signal=opt[1]
                elif (opt[0] == '--help'):
                    print(version)
                    print(usage)
                    sys.exit(0)
                elif (opt[0] == '--test'):
                    _TestMode=1
                elif (opt[0] == '--version'):
                    print(version)
                    sys.exit(0)
                elif (opt[0] == '--?'):
                    print(version)
                    print(usage)
                    sys.exit(0)

        if len(args) > 0:
            _SearchPattern = args[0]
        else:
            raise RuntimeError

    except RuntimeError:
        print(version)
        print("ERROR: Invalid argument or flag found.  Please check your syntax.")
        print("ERROR: Please run again with the --help flag for more information.")
        sys.exit(1)

    except getopt.GetoptError:
        print(version)
        print("ERROR: Invalid argument or flag found.  Please check your syntax.")
        print("ERROR: Please run again with the --help flag for more information.")
        sys.exit(1)

    # Validate the signal we're sending actually exists.
    _Status, _Output = commands.getstatusoutput("kill -l | grep " + _Signal)

    if len(_Output) == 0:
        print("ERROR: No matching signal found for string '" + _Signal + "'.  Perhaps a typo?  Exiting...")
        sys.exit(1)

    # The hunt begins!
    _Status, _Output = commands.getstatusoutput("ps -ef | grep " + _SearchPattern + " | grep -v grep | grep -v sniper.py")

    if _Status != 0:
        print("ERROR: No matching processes found for string '" + _SearchPattern + "'.  Exiting...") 
        sys.exit(1)

    print("INFO:  Found at least one matching process, 'ps -ef' output follows...")
    print("INFO:  " + _Seperator)
    for _Line in _Output.split('\n'):
        print("INFO:  " + _Line)
    print("INFO:  " + _Seperator)

    # Gather target PID list.
    _Status, _Output = commands.getstatusoutput("ps -ef | grep " + _SearchPattern + " | grep -v grep | grep -v sniper.py | awk ' { print $2 } ' | xargs echo")

    if _Status != 0:
        print("ERROR: Caught non-zero exit code from 'ps -ef'.  This shouldn't be possible!  Exiting...")
        sys.exit(2)

    _KillCommand = "kill -s " + _Signal + " " + _Output

    print("INFO:  Target Signal: |" + _Signal + "|") 
    print("INFO:  Target PIDs:   |" + _Output + "|")
    print("INFO:  Kill Cmd:      |" + _KillCommand + "|")
    print("INFO:  " + _Seperator)

    if (_TestMode):
        print("INFO:  Test mode confirmed.  Taking no real action, exiting...")
    else:
        print("INFO:  Sniper mode confirmed.  Sending signals...")

        # Exterminate!
        _Status, _Output = commands.getstatusoutput(_KillCommand)

        print

        if _Status != 0:
            print("ERROR: Caught non-zero exit code kill command.  Output follows...")
            print("ERROR: " + _Seperator)
            for _Line in _Output.split('\n'):
                print("ERROR: " + _Line)
            print("ERROR: " + _Seperator)

            sys.exit(2)

        print("INFO:  Kill command returned success exit code.  Work completed.")

######################################################################
# If called from the command line, invoke thyself!
######################################################################

if __name__=='__main__': main(sys.argv)

######################################################################
