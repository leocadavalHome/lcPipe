from lcPipe.core import database


project = database.getProjectDict()
new = database.getDefaultDict()
print new['workflow']
print project['workflow']
database.updateCurrentProjectKey('workflow', new['workflow'])