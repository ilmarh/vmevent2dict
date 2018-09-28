# -*- coding: utf-8 -*-

from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim
from pyVmomi.VmomiSupport import Object, DataObject, F_LINK, F_LINKABLE, F_OPTIONAL, F_SECRET, ManagedObject
from pyVmomi.VmomiSupport import UncallableManagedMethod, ManagedMethod, binary, Iso8601
import json
from time import sleep
from datetime import date, timedelta, datetime

## Format a python VMOMI object
#
# @param val the object
# @param info the field
# @param indent the level of indentation
# @return the formatted string
def event2nameval(val, info=Object(name="", type=object, flags=0), indent=0):

    name = (info.name and "%s" % info.name or "")

    if val == None:
        result = None
    elif isinstance(val, DataObject):
        if info.flags & F_LINK:
            result = "%s:%s" % (val.__class__.__name__, val.key)
        else:
            result = {}
            for prop in val._GetPropertyList():
                res_name,res_val = event2nameval(getattr(val, prop.name), prop, indent+1)
                # if res_val is not {}, [], None or empty
                if res_val:
                    result.update({res_name:res_val})
    elif isinstance(val, ManagedObject):
        if val._serverGuid is None:
            result = "%s:%s" % (val.__class__.__name__, val._moId)
        else:
            result = "%s:%s:%s" % (val.__class__.__name__, val._serverGuid, val._moId)
    elif isinstance(val, list):
        itemType = getattr(val, 'Item', getattr(info.type, 'Item', object))
        if val:
            item = Object(name="", type=itemType, flags=info.flags)
            result = {}
            for obj in val:
                res_name,res_val = event2nameval(obj, item, indent+1)
                # if res2 is not {}
                if res_val:
                    result.update({res_name: res_val})
        else:
            result = None
    elif isinstance(val, type):
        result = val.__name__
    elif isinstance(val, UncallableManagedMethod):
        result = val.name
    elif isinstance(val, ManagedMethod):
        result = '%s.%s' % (val.info.type.__name__, val.info.name)
    elif isinstance(val, bool):
        result = val and "true" or "false"
    elif isinstance(val, datetime):
        result = Iso8601.ISO8601Format(val)
    elif isinstance(val, binary):
        result = base64.b64encode(val)
        if PY3:
            # In python3 the bytes result after the base64 encoding has a
            # leading 'b' which causes error when we use it to construct the
            # soap message. Workaround the issue by converting the result to
            # string. Since the result of base64 encoding contains only subset
            # of ASCII chars, converting to string will not change the value.
            result = str(result, 'utf-8')
    else:
        result = repr(val).strip("'")

    if name == 'host': name = 'vhost' # For logstash
    return name, result



if __name__ == '__main__':

    VCENTER_HOST = "vcenter" # ChangeIt
    VCENTER_PORT = 443
    VCENTER_USER = "vcenter_adm" # ChangeIt
    VCENTER_PASSWORD = "Very_secret_password" #ChangeIt
    VCENTER_INTERVAL = 10
    si = SmartConnectNoSSL(host=VCENTER_HOST, user=VCENTER_USER, pwd=VCENTER_PASSWORD, port=VCENTER_PORT)
    filter_spec = vim.event.EventFilterSpec()

    eventManager = si.content.eventManager
    event_collector = eventManager.CreateCollectorForEvents(filter_spec)
    last_event_key = 1

    while True:
        try:
            # New events will be inserted at the first element in the collector.latestPage list
            event = event_collector.latestPage[0]
            if last_event_key != event.key:
                name, jdata = event2nameval(event)
                print("Event repr:\n{}\n-------------\nEvent dict():\n{}\n-------------\nEvent json:{}\n".format(event, jdata, (json.dumps(jdata) + '\n').encode('utf-8')))
                last_event_key = event.key
            sleep(float(VCENTER_INTERVAL))

        except:
            raise
