#!/usr/local/bin/python
######################################################################
#
# File: pingtcp.py
#
# Description:  A small script that will attempt a TCP connection to
#               a given host and return simple success or failure status.
#
#               It is known to be able to handle just about any kind of
#               TCP timeout scenario, and will also optionally check for
#               a service banner(i.e. "OpenSSH").
#
# (c) Copyright 2007 Adam W. Dace.  All rights reserved.
#
######################################################################

# Pydoc comments
"""Application entry point for pingtcp."""

# File version tag
__version__ = '1.1'

# Standard modules
import getopt
import os
import os.path
import sys
import socket
import traceback

######################################################################
# Good old main...
######################################################################

def main(argv):
    """Good old main."""

    usage = """Usage: %s [OPTION] host_name

This script attempts to contact a given host_name at a given TCP/IP port.
Using a specified second timeout, it attempts to connect to the remote
host_name and TCP_PORT.  Optionally, it will read a "banner" from the
remote service and return error conditions based on whether it considers
the transaction a success or failure.

The available options are:

    -b=MATCH / --banner=MATCH
    Specifies that in order to achieve success, the remote service
    must return a banner containing the string specified.
    OPTIONAL

    -h / --help / -? / --?
    Prints the usage statement.
    OPTIONAL

    -p=TCP_PORT / --port=TCP_PORT
    Specifies which port on the remote host to connect to.
    Default: 22
    OPTIONAL

    -q / --quiet
    Specifies that only an exit code is wanted.  i.e. no STDOUT output.
    OPTIONAL

    -t / --timeout=TIMEOUT
    Specifies the socket-level timeout in seconds.
    Default: 10
    OPTIONAL

    -v / --version
    Prints the version banner.
    OPTIONAL

Exit Status Codes:
------------------
0 = Success
1 = Socket error type 1.
2 = Socket error type 2.
3 = Socket error type 3.
4 = Socket timeout during connect() / recv().
5 = Unknown exception caught.
6 = Received non-matching or zero-length service banner.

Examples:
---------
pingtcp.py --banner=OpenSSH --timeout=20 sshbox.somewhere.com
pingtcp.py --banner=ESMTP --port=25 mailbox.somewhere.com
""" % argv[0]

    version = """pingtcp.py v%s
Application Layer-based TCP Ping Script
(c) Copyright 2007 Adam W. Dace.  All rights reserved.
------------------------------------------------------
""" % __version__

######################################################################
# Variable initialization.
######################################################################

    # Various variables.
    banner_string = ''
    host_name = ''
    host_port = 22
    timeout = 10
    is_banner_mode = 0
    is_quiet_mode = 0

    # Getopt variables.
    short_options = 'b:hp:qt:v?'
    long_options = ['banner=',
                    'help',
                    'port=',
                    'quiet',
                    'timeout=',
                    'version',
                    '?']

######################################################################
# Main logic flow.
######################################################################

    try:
        if len(argv) < 2:
            raise RuntimeError

        optlist, args = \
                 getopt.getopt(sys.argv[1:], short_options, long_options)

        if len(optlist) > 0:
            for opt in optlist:
                if (opt[0] in ('-b', '--banner')):
                    is_banner_mode = 1
                    banner_string = opt[1]
                elif (opt[0] in ('-h', '-?', '--help', '--?')):
                    print(version)
                    print(usage)
                    sys.exit(0)
                elif (opt[0] in ('-p', '--port')):
                    host_port = int(opt[1])
                elif (opt[0] in ('-q', '--quiet')):
                    is_quiet_mode = 1
                elif (opt[0] in ('-t', '--timeout')):
                    timeout = int(opt[1])
                elif (opt[0] in ('-v', '--version')):
                    print(version)
                    sys.exit(0)

        if len(args) > 0:
            host_name = args[0]

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
        print
        # Displaying original getopt error.
        traceback.print_exc(1, file=sys.stdout)
        sys.exit(1)

    if not is_quiet_mode:
        print(version)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect( (host_name, host_port) )

        # Check for a banner if specified.
        if is_banner_mode:
            remote_banner_string = sock.recv(1024)

            if not is_quiet_mode:
                sys.stdout.write("INFO:  Received remote service header: %d bytes.\n" % len(remote_banner_string))

            if (len(remote_banner_string) < 1):
                if not is_quiet_mode:
                    sys.stderr.write("ERROR: Received zero-length remote service header!\n")
                    sys.exit(6)

            if (remote_banner_string.find(banner_string) == -1):
                sys.stderr.write("ERROR: Received non-matching service banner!\n")
                sys.exit(6)

        sock.close()

        if not is_quiet_mode:
            sys.stdout.write("INFO:  Success!\n")

        sys.exit(0)

    except socket.error, error_info:
        if not is_quiet_mode:
            sys.stderr.write("ERROR: OS Reports: [%s] while connecting to remote host.\n" % (error_info))
            sys.stderr.write("ERROR: Server '" + host_name + "' appears to be down.\n")
        sys.exit(1)

    except socket.herror, (errno, strerror):
        if not is_quiet_mode:
            sys.stderr.write("ERROR: OS Reports: [Errno %s, %s]\n" % (errno, strerror))
            sys.stderr.write("ERROR: Server '" + host_name + "' appears to be down.\n")
        sys.exit(2)

    except socket.gaierror, (errno, strerror):
        if not is_quiet_mode:
            sys.stderr.write("ERROR: OS Reports: [Errno %s, %s]\n" % (errno, strerror))
            sys.stderr.write("ERROR: Server '" + host_name + "' appears to be down.\n")
        sys.exit(3)

    except socket.timeout:
        if not is_quiet_mode:
            sys.stderr.write("ERROR: Socket timed out while connecting to server.\n")
            sys.stderr.write("ERROR: Server '" + host_name + "' appears to be down.\n")
        sys.exit(4)

    except SystemExit:
        sys.exit(0)

    except:
        if not is_quiet_mode:
            sys.stderr.write("ERROR: %s\n" % sys.exc_info()[0])
            sys.stderr.write("ERROR: Server '" + host_name + "' appears to be down.\n")
        sys.exit(5)

######################################################################
# If called from the command line, invoke thyself!
######################################################################

if __name__ == '__main__': main(sys.argv)

######################################################################
