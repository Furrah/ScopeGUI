import vxi11
import telnetlib 
from time import sleep
import numpy as np
import struct
class Oscilloscope:
    def __init__(self,hostname):
        self.hostname = hostname 
        self.instr = vxi11.Instrument(self.hostname)
        # self.scopeSetup()
        # self.channelSetup("C1")
        # self.channelSetup("C2")

    def channelSetup(self,channel):
        self.instr.write(channel +':VOLT_DIV 200MV')
        self.instr.write(channel +':COUPLING D50')


    def setupVoltDiv(self,channel,volt_div):
         self.instr.write(channel +':VOLT_DIV ' + volt_div)       


    def triggerLevel(self,channel,trigger):
        self.instr.write(channel +':TRIG_LEVEL '+ trigger)     

    def scopeSetup(self):

        self.instr.write('C1:TRIG_LEVEL 100MV') # This assumes Channel 1 is the high gain channel
        self.instr.write('INTERLEAVED ON') #enable RIS
        self.instr.write('TIME_DIV 5NS')


    def getData(self,channel):
        self.instr.write('CHDR OFF')
        self.instr.write('CFMT DEF9,WORD,BIN')
        self.instr.write(channel +':WAVEFORM? DAT1')
        dat = self.instr.read_raw()
        dat_str = np.array(struct.unpack('16x {0}h x'.format((len(dat)-17)//2), dat))
        gain = float(self.instr.ask(channel +":INSPECT? \"VERTICAL_GAIN\"")[1:-1].split(":")[1].strip())
        v_offs = float(self.instr.ask(channel +":INSPECT? \"VERTICAL_OFFSET\"")[1:-1].split(":")[1].strip())
        h_offs = float(self.instr.ask(channel +":INSPECT? \"HORIZ_OFFSET\"")[1:-1].split(":")[1].strip())
        h_interval = float(self.instr.ask(channel +":INSPECT? \"HORIZ_INTERVAL\"")[1:-1].split(":")[1].strip())

        data = np.array(dat_str) * gain - v_offs
        
        t = np.arange(0,len(data))
        t = h_interval*t + h_offs
        
        out = np.array([t,data])
        return out

    def clearSweeps(self):
        self.instr.write('CLEAR_SWEEPS')
        self.instr.write('DD_RESET_AVERAGE')

class RF_Switch:
    def __init__(self,hostname):
        self.hostname = hostname 

    def telnet_exec_cmd(self,cmd):
        tn = telnetlib.Telnet(self.hostname,23,timeout = 10)
        tn.write(bytes('{0}\n'.format(cmd), 'UTF-8'))
        res = tn.read_until(b'\n')
        res = tn.read_until(b'\n')
        tn.close()
        return res

    def resetSwitches(self):
        state = self.telnet_exec_cmd(b'SETP=0\n')
        sleep(0.1)


        if int(state) == 1:
            print("switches reset successfully")
            return 1

        elif int(state == 0):
            print("reset switches failed")

        elif int(state == 4):
            print('Switch not set (invalid switch state requested)')

        
    def setSwitches(self,beam):
        state = self.resetSwitches()
        beam_type = {'ultimate':0, 'nominal':1, 'pilot':2, 'single':3}

        if state == 1:
            if beam_type[beam] == 0:

                self.telnet_exec_cmd(b'SETA=1\n')
                sleep(1)
                self.telnet_exec_cmd(b'SETE=1\n')
                print('ultimate beam set')          

            elif beam_type[beam] == 1:
                
                self.telnet_exec_cmd(b'SETB=1\n')
                sleep(1)
                self.telnet_exec_cmd(b'SETF=1\n')   
                print('nominal beam set')   

            elif beam_type[beam] == 2:
                
                self.telnet_exec_cmd(b'SETC=1\n')
                sleep(1)
                self.telnet_exec_cmd(b'SETG=1\n')   
                print('pilot beam set') 

            elif beam_type[beam] == 3:

                self.telnet_exec_cmd(b'SETD=1\n')
                sleep(1)
                self.telnet_exec_cmd(b'SETH=1\n')   
                print('single beam set')    
            else:
                print("switches not set")

    def getSwitchState(self):
        res = self.telnet_exec_cmd(b'SWPORT?')

        switch_states = [17,34,68,136]
        beam_type = {17:'ultimate', 34:'nominal', 68:'pilot', 136:'single'}


        print('switch state', beam_type[int(res)])



        return int(res)

class Func_Gen:
    def __init__(self,hostname):
        self.setup(hostname)

    def setup(self,hostname):
        # self.instr = vxi11.Instrument(hostname)
        self.instr = vxi11.Instrument('CFB-866-WG2')
        self.instr.write("OUTPUT1 OFF")

        self.pulseShape()

    def pulseShape(self):
        self.instr.write('SOURCE1:FUNCTION PULSE')
        self.instr.write("SOURCE1:FUNCTION:PULSE:WIDTH 20E-9")
        self.instr.write("SOURCE1:FUNCTION:PULSE:TRANSITION:BOTH 8.4e-9")       
        self.instr.write("SOURCE1:FREQUENCY 1e5")
        self.instr.write("SOURCE1:VOLT 1")


    def trigger(self,state):
        if state ==1:
            self.instr.write("OUTPUT1 ON")

        elif state == 0:
            self.instr.write("OUTPUT1 OFF")
            
    def getState(self):
        raw = self.instr.ask("OUTPUT1?")
        print('function generator output1 state: {}'.format(int(raw)))
        return(int(raw))