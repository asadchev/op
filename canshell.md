Canbus/panda shell

Commands
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
