# vmevent2dict
Convert VMWare VCenter Events to dict() -- easy serializable. Derived from pyVmomi.Support.Format().

name, val event2nameval(vim.event.Event):

Usage is simple -- just feed in Event recieved from vcenter and recieve this event like dict() in val. name wil be empty
