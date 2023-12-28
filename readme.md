# Usage

A utility to run a given command against a set of tests expressed as pairs of
files. File pairs are input and output files. The command is executed with the
standard input from the input file. The standard output is then compared with
the output file.

This is used to test competitive programming solutions, which often provide
test files and use standard input and output for the communication.

# Integration

## Vim

A Vim script might be added here one day...

A general idea is to put test files and a solution source in the same
directory; bind the compilation command (if needed) to compile the solution
file (can use `tempname()` to keep the solution directories cleaner); bind
another command to run the test utility for the solution file's directory. The
target solution file can be the one in the current buffer - this can allow to
switch quickly between multiple solutions.
