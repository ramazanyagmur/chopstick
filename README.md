# chopstick
Parser for cfgmml format

It is aimed for parsing cfgmml files to be converted to a column based format.
It needs a default file "infiledef.txt" for output to be configured and standardized for multiple input files.
And it needs a filler file "inprefill.txt" to create an extra column (like cellname), based on another MOC.
Then will read all files from in/ directory and output to out/ directory.
