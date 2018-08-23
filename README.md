# lcPipe

dependencias:
pymongo 3.6
(pip install pymongo)

maya 2015 ou +
O maya precisa enxergar o pymongo

mongoBD 3.6 Community
https://www.mongodb.com/download-center?jmp=tutorials#community

A database mongoDB pode rodar local 
https://docs.mongodb.com/manual/administration/install-community/

Instalar junto o mongoDB Compass (viewer)
É preciso criar uma database chamada lcPipeline e dentro um collection chamado projects

Pra rodar a pipeline:

##
import lcPipe.main as pipe
reload (pipe)
x = pipe.Session()
x.createMenu()
##

Um menu novo é criado. Escolher browser
