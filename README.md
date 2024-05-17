# bein - better input

## About
Tool for parsing specific escape sequences and providing them as input in place to a process.
Useful for purposes where raw bytes need to be sent to a process as input i.e. binary exploitation

## Usage
```
python pwni.py [-h] [-o <file>] [-v] [-a] [-l] [-n] [-p <process>]
```

## Options
```
  -h           : Show this help message and exit
  -o <file>    : Write output to file instead of stdout
  -v           : Be verbose, prints all exceptions and errors
  -a           : Only output standard keyboard characters (ascii 32-127)
                 Anything else will be written as [0x??]
  -l           : Use little endian byte order when parsing hex values initialized with \0x
  -n           : Strip newline from input
  -p <process> : Run the specified process and parse input before sending it to the process
                 To pass additional arguments to the process itself,
                 use quotes around the command: -p 'ls -al'
                 Alternatively, use: -p bash or: -p sh and run commands from the shell
```

## Requirements
```
prompt_toolkit
pwntools
```
This tool heavily depends on pwntools ability to handle I/O of processes and prompt toolkit
for a nicer command line experience, allowing you to use the arrow keys like in bash and
auto completions based on your input history.
