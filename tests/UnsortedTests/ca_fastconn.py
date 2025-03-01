from epics import ca, dbr
from epics.utils import IOENCODING
import time
import debugtime
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict
dt = debugtime.debugtime()
def add(x):
    print(x)
    dt.add(x)

add('test of fast connection to many PVs')
pvnames = []

results = OrderedDict()

MAX_PVS = 12500

for line  in open('fastconn_pvlist.txt','r', encoding=IOENCODING).readlines():
    if not line.startswith('#'):
        pvnames.append(line.strip())

if MAX_PVS is not None:
    pvnames = pvnames[:MAX_PVS]


add('Read PV list:  Will connect to %i PVs' % len(pvnames))
libca = ca.initialize_libca()

for name in pvnames:
    chid = ca.create_channel(name, connect=False, auto_cb=False)
    results[name] = {'chid': chid}

time.sleep(0.001)

add("created PVs with ca_create_channel")

for name in pvnames:
    ca.connect_channel(results[name]['chid'])

time.sleep(0.001)

add("connected to PVs with connect_channel")

ca.pend_event(1.e-2)

for name in pvnames:
    chid = results[name]['chid']
    val = ca.get(chid, wait=False)
    results[name]['value'] =  val

add("did ca.get(wait=False)")
ca.poll(2.e-3, 1.0)
add("ca.poll() complete")

for name in pvnames:
    results[name]['value'] = ca.get_complete(results[name]['chid'])

add("ca.get_complete() for all PVs")

f = open('fastconn_pvdata.sav', 'w')
for name, val in results.items():
    f.write("%s %s\n" % (name.strip(), val['value']))
f.close()
add("wrote PV values to disk")

dt.show()

time.sleep(0.01)
ca.poll()
