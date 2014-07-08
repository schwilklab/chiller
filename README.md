README: chiller.py
==================

Code to run a temperature profile program on the Thermo-Fisher refrigerated bath.


## Command line options ##

The program takes two optional command line options:

- `-i` sets the update interval (default is 10 seconds)
- `-p` gives a program file (default is 'ch-run.txt')


## Program file format ##

- The first line gives the name of the program (the "run ID"): the first token is ignored and the second is the name.
- every subsequent line has two whitespace-separated values: the first column is a time in minutes and the second column is a temperature in degrees C.

The time indicates the number of minutes the program should take to get from the current temperature to the one indicated.

There is one exception: in the the first line of data, the time entry is ingored (and can be zero). The first entry indicates the "starting temp."  The program will attempt to bring the water bath to this temperature as quickly as possible, regardless of the time indicated.  The program will NOT move on to the next time/temperature until this starting temperature has been reached.

After this point, the program proceeds. It is important to not put in a shorter time than the system is capable of. For example, if the current temperature is -10C and the next step indicates 5 minutes to move to -25C (line = "5  -25.0"), then after 5 minutes, the program will move on to the next step even if the temperature has not been reached.

An example program file:

```
RUNID standard
0    4.0
50 0.0
25 -2.0
25 -4.0
25 -6.0
25 -8.0
25 -10.0
25 -12.0
```
