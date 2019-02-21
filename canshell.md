Canbus/panda shell, small wrapper around `panda.Panda` to recv and send to CanBus.\
Useful to figure what different CAN messages are.  \
Needs `pyparsing` to run.

Start it, `./canshell.py`, and once panda is connected, you'll get prompt `> `.\
To quit, do `Ctrl-D`, to see help, do `help`, to interrupt command, do `Ctrl-C`. 

Some commands
* `safety` - set safety \
  eg `safety elm327`
* `recv [0xid[,...]]` - receive can message(s) \
  eg `recv`, `recv 0x152`, `recv 0x152, 0x153`
* `send 0xid,0xdata,bus` - send can message \
  eg `send 0x152,0xDEADBEEFDEADBEEF,0`
* `ignore 0xid[,...]` - add id(s) to `recv` ignore list \
  eg `ignore 0x152`
* `baseline` - record baseline activity ignored by `recv`
* `discover` - discover can traffic
  * `discover`                 - print unique ids
  * `discover 0xid[,...]`      - print unique messages from id(s)
  * `discover 0xid mask 0xmask` - print unique messages from id with mask applied to data \
     eg `discover 0x152 mask 0xFF0F` will treat `0xFF*F...` as `0xFF0F...` 

Example session:
```
> andrey@andrey-ThinkPad-S1-Yoga:~/asadchev.github/op$ ./canshell.py
Panda/CanBus shell:
Ctrl-C - interrupt running command
Ctrl-D - exit canshell
 ! <expr> - evaluate python expression
 help - list commands
 help <command> - command help

Trying to connect to Panda over USB...
USB connection failed. Trying WiFi...
opening WIFI device
connected
> clear 0
> discover
0x152
0x188
0x156
0x3d1
0x282
0x660
0x6d1
0x375
0x374
^C
> discover 0x188
0x188, 0x0300000000000000, 0
0x188, 0x0000020001070000, 0
0x188, 0x0000040001070000, 0
0x188, 0x0000060001070000, 0
0x188, 0x0000080001070000, 0
0x188, 0x00000a0001070000, 0
0x188, 0x00000c0001070000, 0
0x188, 0x00000e0001070000, 0
0x188, 0x0000000001070000, 0
^C
> discover 0x188 mask 0xfffff0
0x188, 0x0000000001070000, 0
0x188, 0x0300000000000000, 0
^C
> safety
ALLOUTPUT        CHRYSLER         FORD             HONDA            HYUNDAI          TESLA            TOYOTA_IPAS
CADILLAC         ELM327           GM               HONDA_BOSCH      NOOUTPUT         TOYOTA           TOYOTA_NOLIMITS
> safety T
TESLA            TOYOTA           TOYOTA_IPAS      TOYOTA_NOLIMITS
> safety ALLOUTPUT
> send 0x188, 0x0000040001070000, 0
> send 0x188, 0x0000040001070000, 0 freq 10
^C
```
