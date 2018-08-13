from lcPipe.core import database
from lcPipe.api.item import Item

project = database.getProjectDict()
new = database.getDefaultDict()
print new['workflow']
print project['workflow']
database.updateCurrentProjectKey('workflow', new['workflow'])


item = Item(task='proxy', code='0053', itemType='asset')
print item.components