from lcPipe.api.item import Item
from lcPipe.api.xloComponent import XloComponent
from lcPipe.api.cacheComponent import CacheComponent

item = Item(task='render', code='0001')

ns = 'ref'
src = item.components[ns]
xlo = XloComponent(ns, src, item)
cache = CacheComponent(ns, src, item)


cacheItem = cache.getItem()
print cache.getPublishPath()
print cacheItem.getDataDict()

xloItem = xlo.getItem()

print xlo.checkForNewVersion()
print xloItem.getDataDict()