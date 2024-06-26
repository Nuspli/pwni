#!/usr/bin/python3

import sys
import traceback

OUTFILE = None
output = None
VERBOSE = False
ASCII_ONLY = False
ASCII_ONLY_NEWLINE = False
BYTEORDER = 'big'
STRIP_NEWLINE = False
PROCESS = None

def ascii_only(data):
    for b in data:
        if not (b >= 32 and b <= 127 or (ASCII_ONLY_NEWLINE and (b == 10 or b == 13))):
            data = data.replace(bytes([b]), b'[' + bytes(hex(b), encoding='utf-8') + b']')
    return data

def write_stdout(data):

    if ASCII_ONLY:
        data = ascii_only(data)
    
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

def write_file(data):

    if ASCII_ONLY:
        data = ascii_only(data)

    OUTFILE.write(data)
    OUTFILE.flush()

def parse(input):

    out = bytearray()

    i = 0
    l = len(input)

    while i < l:

        if chr(input[i]) == '\\' and i+1 < l:

            if chr(input[i+1]) == 'x':
                if i+3 < l:
                    try:
                        value = int(input[i+2:i+4], 16)
                        out.append(value)
                        i += 3

                    except ValueError:
                        out.append(input[i])
                        if VERBOSE:
                            print("[Invalid byte value]")
                            traceback.print_exc()
                else:
                    out.append(input[i])

            elif chr(input[i+1]) == 'n':
                out.append(ord('\n'))
                i += 1

            elif chr(input[i+1]) == 'r':
                out.append(ord('\r'))
                i += 1

            elif chr(input[i+1]) == '0':
                if chr(input[i+2]) == 'x' and i+3 < l:
                    a = 0
                    while i+3+a < l and chr(input[i+3+a]).isalnum():
                        a += 1
                    try:
                        hex_bytes = int(input[i+3:i+3+a], 16).to_bytes((a+1)//2, byteorder=BYTEORDER)
                        out.extend(hex_bytes)
                        i += 2+a

                        if i+1 < l and input[i+1] == ord('\\'):
                            i += 1

                    except ValueError:
                        out.append(input[i])
                        if VERBOSE:
                            print("[Invalid hex value]")
                            traceback.print_exc()
                else:
                    out.append(ord('\0'))
                    i += 1

            else:
                out.append(input[i])
        else:
            out.append(input[i])

        i += 1

    return bytes(out)

def parse_process_args(args):
    
    i = 0
    while i < len(args):
        if args[i].startswith('\"'):
            for j in range(i+1, len(args)):
                if args[j].endswith('\"'):
                    args[i] = ' '.join(args[i:j+1]).replace('\"', '')
                    args = args[:i+1] + args[j+1:]
                    break
                
        if args[i].startswith('\''):
            for j in range(i+1, len(args)):
                if args[j].endswith('\''):
                    args[i] = ' '.join(args[i:j+1]).replace('\'', '')
                    args = args[:i+1] + args[j+1:]
                    break
        i += 1

    return args

def tty_mode():

    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.history import FileHistory
    import os

    history_path = os.path.expanduser('~/.bein_history')
    if not os.path.exists(history_path):
        os.close(os.open(history_path, os.O_CREAT))

    session = PromptSession(history=FileHistory(history_path), auto_suggest=AutoSuggestFromHistory())
    thread = None

    if PROCESS:
        from pwn import process
        import threading

        args = parse_process_args(PROCESS.split())

        p = process(args, level='debug' if VERBOSE else 'error')

        def print_output():

            while True:
                try:
                    output(p.recv())

                except:
                    print("\nProcess exited")
                    p.close()

                    if VERBOSE:
                        traceback.print_exc()

                    break

        thread = threading.Thread(target=print_output)
        thread.start()

    while True:
        try:
            line = session.prompt()

            if not STRIP_NEWLINE:
                line += '\n'

            line = bytes(line, 'utf-8')
            parsed = parse(line)
            
            if PROCESS:
                if not p.connected():
                    break
                p.send(parsed)

            else:
                output(parsed)

        except:
            if PROCESS:
                p.close()
            
            if VERBOSE:
                traceback.print_exc()

            break
    if thread:
        thread.join()

def set_arguments():
    
    args = sys.argv[1:]

    if '-h' in args or '--help' in args:
        print("Usage:")
        print(f"  python {sys.argv[0]} [-h] [-o <file>] [-v] [-a] [-an] [-l] [-r] [-p <process>]\n")

        print("About:")
        print("  Tool for parsing specific escape sequences and providing them as input in place to a process")
        print("  Useful for purposes where raw bytes need to be sent to a process as input i.e. binary exploitation\n")

        print("Options:")
        print("  -h           : Show this help message and exit")
        print("  -o <file>    : Write output to file instead of stdout")
        print("  -v           : Be verbose, prints all exceptions and errors")
        print("  -a           : Only output standard keyboard characters (ascii 32-127)")
        print("                   Anything else will be written as [0x??]")
        print("  -an          : Like -a except allow newline characters too")
        print("  -l           : Use little endian byte order when parsing hex values initialized with \\0x")
        print("  -r           : Raw input, strips newline characters from the input")
        print("  -p <process> : Run the specified process and parse input before sending it to the process")
        print("                   To pass additional arguments to the process itself")
        print("                   use quotes around the command: -p \'ls -al\'")
        print("                   Alternatively, use: -p bash or: -p sh and run commands from the shell")
        exit(0)

    global OUTFILE
    global output
    global VERBOSE
    global ASCII_ONLY
    global ASCII_ONLY_NEWLINE
    global BYTEORDER
    global STRIP_NEWLINE
    global PYTHON_MODE
    global PROCESS

    if '-o' in args:
        OUTFILE = open(args[args.index('-o') + 1], 'wb')
        output = write_file

    if '-v' in args:
        VERBOSE = True

    if '-a' in args:
        ASCII_ONLY = True

    if '-an' in args:
        ASCII_ONLY = True
        ASCII_ONLY_NEWLINE = True

    if '-l' in args:
        BYTEORDER = 'little'

    if '-r' in args:
        STRIP_NEWLINE = True

    if '-p' in args:
        PROCESS = args[args.index('-p') + 1]

if __name__ == '__main__':

    output = write_stdout
    set_arguments()

    if sys.stdin.isatty() and sys.stdout.isatty():
        tty_mode()

    else:
        for line in sys.stdin.buffer:

            if STRIP_NEWLINE:
                line = line.rstrip()

            output(parse(line))
"""
requirements:

pip install prompt_toolkit
pip install pwntools
"""