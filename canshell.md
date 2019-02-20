Canbus/panda shell

Commands
* safety                - safety elm327
* recv [0xid[,...]]     - recv 0x152
* send 0xid,0xdata,bus  - send 0x152,0xDEADBEEFDEADBEEF,0
* ignore 0xid[,...]     -  ignore 0x152
* baseline
  - record baseline activity ignored by recv
* discover
  > discover                  - print unique ids
  > discover 0xid[,...]       - print unique messages from id
  > discover 0xid mask 0xmask - print unique messages from id with mask applied to data