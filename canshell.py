#!/usr/bin/env python2.7

import readline, sys, time
import cmd
import pyparsing as pp
import binascii
from panda import Panda

readline.parse_and_bind('tab: complete')

def _parse_ids(args):
    if not args: return None
    hexs = pp.Combine(pp.Literal("0x") + pp.Word(pp.hexnums))    
    id = hexs('ids*')
    grammar = id + pp.ZeroOrMore(pp.Optional(",") + id)
    r = grammar.parseString(args, parseAll=True)
    return [ int(i,16) for i in r.ids] 

def format(id, data, bus):
    return "0x%x, 0x%s, %i" % (id, binascii.hexlify(data), bus)

def _parse_discover_args(args):
    if not args.strip():
        return (None,[])
    hexs = pp.Combine(pp.Literal("0x") + pp.Word(pp.hexnums))
    id = hexs('ids*')
    grammar = (id + pp.ZeroOrMore(pp.Optional(",") + id)) + pp.Optional(pp.Literal("mask") + hexs('mask'))
    r = grammar.parseString(args, parseAll=True)
    ids = [ int(i, 16) for i in r.ids ]
    mask = []
    if r.mask:
        mask = bytearray.fromhex(r.mask[2:])
    return (ids,mask)

def _parse_send_args(args):
    hexs = pp.Combine(pp.Literal("0x") + pp.Word(pp.hexnums))
    msg = (hexs + pp.Suppress(",") + hexs + pp.Suppress(",") + pp.Word(pp.nums))("msgs*")
    grammar = pp.OneOrMore(msg) + pp.Optional(pp.Literal("freq") + pp.Word(pp.nums)('freq'))
    r = grammar.parseString(args, parseAll=True)
    msgs = [ (int(id,16), bytearray.fromhex(data[2:]), int(bus)) for (id,data,bus) in r.msgs ]
    freq = None
    if r.freq: freq = float(r.freq)
    return (msgs, freq)
    
class canshell(cmd.Cmd):

    prompt = '> '

    def __init__(self):

        print "Panda/CanBus shell:"
        print "Ctrl-C - interrupt running command"
        print "Ctrl-D - exit canshell"
        print (" ! <expr> - evaluate python expression")
        print (" help - list commands")
        print (" help <command> - command help")
        print ("")

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

    def do_shell(self, args):
        "Evaluate Python expression."
        panda = self.panda
        def send(id, msg, bus): panda.can_send(id, msg, bus)
        def recv(): return panda.can_recv()
        print eval(args)
        
    def do_clear(self, args):
        "clear panda buffer, requires int arg"
        self.panda.can_clear(int(args))
        
    def do_safety(self, args):
        "set panda safety level"
        s = eval("Panda.SAFETY_%s" % args.upper())
        self.panda.set_safety_mode(s)

    def complete_safety(self, text, line, begidx, endidx):
        v = [
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
        k = line[begidx:endidx].upper()
        return [ s for s in v if s.startswith(k) ]
        
    def do_baseline(self, args):
        "record baseline ignored in recv"
        while True:
            msgs = self.panda.can_recv()
            for (id, _, dat, src) in msgs:
                msg = (id, dat, src)
                self.__baseline__.add(msg)

    def do_ignore(self, args):
        "ignore given ids in recv"
        for a in _parse_ids(args):
            self.__ignore__.add(a)
            
    def do_discover(self, args):
        """
        discover unique ids or messages with optional hex mask
        Examples:
          discover
          discover 0x152
          discover 0x152 mask 0x0f0f
        """
        (ids,mask) = _parse_discover_args(args)
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
        """
        recv from any or from given address(es)
        Examples:
          recv
          recv 0x152
          recv 0x374,0x374
        """
        
        ids = _parse_ids(args)
        while True:
            msgs = self.panda.can_recv()
            for (id, _, data, src) in msgs:
                if not ids:
                    if id in self.__ignore__: continue
                    if (id, data, src) in self.__baseline__: continue
                else:
                    if not id in ids: continue
                print (format(id, data, src))

    def do_send(self, args):
        """
        send one or more messages once or with given frequency
        Examples:
          send 0x375,0xffffffffffffffff,0
          send 0x375,0xffffffffffffffff,0 0x375,0x0000000000000000,0
          send 0x375,0xffffffffffffffff,0 freq 10
        """
        (msgs, freq) = _parse_send_args(args)
        while True:
            for (id,data,bus) in msgs:
                #print (format(id, data, bus))
                self.panda.can_send(id, data, bus)
            if freq:
                time.sleep(1.0/freq)
                continue
            break

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
    canshell().cmdloop()
