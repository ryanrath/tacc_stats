#!/usr/bin/env python
import sys
import csv

class StampedeAccountFixer:
    def __init__(self, infilename, outfilename):

        self.delimiter = ":"
        self.expectedfields = 12

        self.infilename = infilename
        self.outfp = open(outfilename, "wb")
        self.writer = csv.writer(self.outfp, delimiter=self.delimiter, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        self.lastfields = 0
        self.linenumber = 0

        self.parse()

    def addtokens(self, tokens):
        if self.lastfields != 0:
            raise Exception("Discarding data on line: {}".format(self.linenumber))

        self.writer.writerow(tokens)

    def addline(self, line):
        self.addtokens(line.strip().split(self.delimiter))

    def parse(self):

        last = ""
        self.linenumber = 0
        with open(self.infilename, "rb") as fp:
            for line in fp:
                self.linenumber += 1
                fields = line.count(self.delimiter)
                if fields < self.expectedfields:
                    last += line
                    self.lastfields += fields

                    if self.lastfields == self.expectedfields:
                       self.lastfields = 0
                       self.addline(last)
                       last = ""

                elif fields > self.expectedfields:
                    tokens = line.strip().split(self.delimiter)
                    result = tokens[0:9]
                    result.append( self.delimiter.join(tokens[9:fields-2]) )
                    result.extend( tokens[fields-2:] )
                    self.addtokens(result)

                else:
                    self.addline(line)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Usage {} INFILE OUTFILE".format(sys.argv[0])
        sys.exit(1)

    s = StampedeAccountFixer(sys.argv[1], sys.argv[2])
