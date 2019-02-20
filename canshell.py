#!/usr/bin/env python2.7

import readline, sys, cmd
from panda import Panda
import re
import binascii

readline.parse_and_bind('tab: complete')

def recv():
    return random.randint(0, 100)

def tokenize(s):
    tokens = []
    for t in re.split('[, ]', s):
        t = t.strip()
        if t: tokens.append(t)
    return tokens;

def format(id, data, bus):
    return "0x%x, 0x%s, %i" % (id, binascii.hexlify(data), bus)

class canwatch(cmd.Cmd):

    #intro = "Canwatch, Ctrl-D to quit"
    prompt = '> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.__baseline__ = set()
        self.__ignore__ = set()

        try:
            print("Trying to connect to Panda over USB...")
            self.panda = Panda()

        except AssertionError:
            print("USB connection failed. Trying WiFi...")

        #self.panda = None
        try:
            self.panda = Panda("WIFI")
        except:
            print("WiFi connection timed out. Please make sure your Panda is connected and try again.")
            sys.exit(0)

        self.panda.can_clear(0)


    def do_EOF(self, args):
        sys.exit(0)

    def do_safety(self, args):
        s = eval("Panda.SAFETY_%s" % args.upper())
        self.panda.set_safety_mode(s)

    def complete_safety(self, text, line, begidx, endidx):
        return [
            "NOOUTPUT",
            "HONDA",
            "TOYOTA",
            "GM",
            "HONDA_BOSCH",
            "FORD",
            "CADILLAC",
            "HYUNDAI",
            "TESLA",
            "CHRYSLER",
            "TOYOTA_IPAS",
            "TOYOTA_NOLIMITS",
            "ALLOUTPUT",
            "ELM327",
        ]
        
    def do_baseline(self, args):
        while True:
            msgs = self.panda.can_recv()
            for (id, _, dat, src) in msgs:
                msg = (id, dat, src)
                self.__baseline__.add(msg)

    def do_ignore(self, args):
        for a in tokenize(args):
            try:
                self.__ignore__.add(int(a, 16))
            except Exception, e: print e

    def _parse_discover_args(self, args):
        args = args.lower().split(" mask ", 1)
        ids = None
        mask = []
        if args:
            ids = set([ int(a, 16) for a in tokenize(args[0]) ])
        if len(args) == 2:
            mask = bytearray.fromhex(args[1].strip()[2:])
        return (ids,mask)
            
    def do_discover(self, args):
        (ids,mask) = self._parse_discover_args(args)
        seen = set()
        while True:
            msgs = self.panda.can_recv()
            for (id, _, data, src) in msgs:
                if ids:
                    data = bytearray(data)
                    for i,b in enumerate(mask):
                        data[i] &= b
                    if id not in ids: continue
                    k = (id,str(data),src)
                    if k in seen: continue
                    print (format(*k))
                    seen.add(k)
                else:
                    if id in seen: continue
                    print (hex(id))
                    seen.add(id)
            
    def do_recv(self, args):
        ids = set([ int(a, 16) for a in tokenize(args) ])
        while True:
            msgs = self.panda.can_recv()
            for (id, _, data, src) in msgs:
                if not ids:
                    if id in self.__ignore__: continue
                    if (id, data, src) in self.__baseline__: continue
                else:
                    if not id in ids: continue
                print (format(id, binascii.hexlify(data), src))

    def do_send(self, args):
        (id, data, bus) = tokenize(args)
        id = int(id,16)
        data = bytearray.fromhex(data.strip()[2:])
        bus = int(bus)
        #print (format(id, binascii.hexlify(data), bus))
        self.panda.can_send(id,data,bus)

    def onecmd(self, line):
        try:
            return cmd.Cmd.onecmd(self, line)
        except Exception, e:
            print e
            return False # don't stop
        
    def cmdloop(self):
        while True:
            try: cmd.Cmd.cmdloop(self)
            except KeyboardInterrupt:
              print
              continue

    # while True:
    #     try:
    #         line = raw_input("> ")
    #         if not line.strip(): continue
    #         try:
    #             exec(line) in globals(), locals()
    #         except Exception, e:
    #             print e
    #     except KeyboardInterrupt:
    #         continue


if __name__ == '__main__':
    canwatch().cmdloop()
