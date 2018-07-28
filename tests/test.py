import lcPipe.api.item as it
import  lcPipe.api.xloComponent as xlo
from lcPipe.api.cacheComponent import CacheComponent
import lcPipe.api.sceneSource as ss
import lcPipe.core.check as ck

import lcPipe.api.component as cp


reload(ss)
reload(ck)
reload (it)
reload (cp)
reload (xlo)


item = it.Item(task='render', code='0001')
print item.getDataDict()
x = cp.Component('ref', item.components['ref'], parent=item)

print x.getDataDict()

x.cacheVer = 8

x.putToParent()