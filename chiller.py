#!/usr/bin/env python
# chiller.py
"""
Communicate with Thermo Refrigerated Bath
"""

__version__ = "0.1"

import sys, serial, time, logging

comport = "/dev/ttyUSB0"
baud = 19200
INTERVAL = 10 # default interval
ACCURACY = 0.08  # C
VARIANCE = 0.08

PROG_FILE = "./ch-run.txt"  # default

chiller_logger = logging.getLogger('chiller_logger')
info_logger = logging.getLogger('info_logger')

LOGFILE = "chiller-log.log"

loghandler = logging.FileHandler(LOGFILE)
loghandler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
chiller_logger.addHandler(loghandler)
chiller_logger.setLevel(logging.INFO)

infohandler = logging.StreamHandler(sys.stdout)
infohandler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
info_logger.addHandler(infohandler)
info_logger.setLevel(logging.DEBUG)

def read_program(fname):
    f = open(fname, "r")
    lines = f.readlines()
    pname = lines[0].split()[-1]
    times = []
    temps = []
    for l in lines[1:]:
        try :
            t, c = l.split()
            times.append(float(t))
            temps.append(float(c))
        except:
            chiller_logger.warning("Bad or empty line in program file: %s" % l)
    return (pname, times, temps)

        
class Chiller:
    def __init__(self, ser, interval):
        self.ser = ser
        self.interval = interval
        self.temps = []
        self.times = []

    def read_value(self, par):
        self.ser.write("R%s\r" % par)
        s = self.ser.readline()[0:-1]
        if s[0] == "?" :
            val = "FAILURE"
            chiller_logger.warning("FAILED READ of %s: %s" % (par, s))
        else :
            chiller_logger.info("VALUE RECEIVED: %s" % s)
        return (s)
            
    def write_value(self, par, val):
        self.ser.write("S%s %s\r" % (par, val))
        s = self.ser.readline()[:-1]
        if s[0:2] == "OK" :
            chiller_logger.info("WRITE SUCCESSFUL: %s %s" % (par,val))
        else : #if s[0] == "$" :
            chiller_logger.warning("WRITE FAILURE: %s %s, %s" % (par,val, s))
        return(s)

    def set_temp(self, temp):
        r = self.write_value("S", str(temp))
        #chiller_logger.info("set temp response: " + r)
        return

    def read_temp(self):
        t = self.read_value("T")
        try:
            return(float(t[0:-1]))
        except:
            return(t)
    
    def on(self):
        r = self.write_value("O", "1")
        return(r)

    def off(self):
        r = self.write_value("O", "0")
        return(r)

    def bring_to_temp(self, temp):
        self.set_temp(temp)
        t = self.read_temp()
        while abs(t - temp) > ACCURACY :
            info_logger.info("SetPoint:" + "\t" +  str(temp) + "\tTemp:\t" + str(self.read_temp()))
            time.sleep(self.interval)
            t = self.read_temp()

        return

    def set_ramp(self, ramp, times, temps):
        n = len(times) - 1
        program = "%d %0.2f %d %0.2f"  % (n, VARIANCE, 1, temps[0] )
        self.write_value("RP" , program)
        for i in range(1,n+1) :
            self.write_value("RS" , "%d %0.2f %d" % (i, temps[i], times[i]))
        return

                                

    def run_program(self, times, temps):
        info_logger.info("Running Program. Interval: " + str(INTERVAL))
        self.set_ramp(1, times, temps)
        self.on()
        self.bring_to_temp(temps[0])
        
        self.write_value("RO", "S")
        while(True):
            info_logger.info("Temp:\t" + str(self.read_temp()))
            time.sleep(self.interval)
            if self.read_value("RO") != "Running" : break

        info_logger.info("Program finished")
        return

    
  
def main():
    """Command-line tool.  See chiller.py -h for help.
    """
    #set default input and output
    #input = sys.stdin
    #output = sys.stdout

    from optparse import OptionParser

    usage = """
    usage: %prog [options]
    """

    parser = OptionParser(usage=usage, version ="%prog " + __version__)
    # parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
    # 				  help="Print INFO messages to stdout, default=%default")
    parser.add_option("-i", "--interval", type="int", dest="interval", default=INTERVAL,
                                      help="Set update interval in seconds, default=%default")
    parser.add_option("-f", "--progfile", type="str", dest="progfile", default=PROG_FILE,
                                      help="Set program file, default=%default")

    (options, args) = parser.parse_args()


    ser = serial.Serial(comport, baud, timeout=1)
    chil = Chiller(ser, interval = options.interval)

    chiller_logger.info("Program started")
    # start by turning everything off:
    chil.write_value("RO", "E")
    chil.off()
        

    pname, times, temps = read_program(options.progfile)
    info_logger.info("Running Program: " + pname)
    chil.run_program(times, temps)

    chiller_logger.info("Program ended")

if __name__=="__main__":

    main()
    
