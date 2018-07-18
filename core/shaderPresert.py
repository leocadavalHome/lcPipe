import pymel.core as pm


def getGeoGroupMembers(geoGroup):
    geosShape = geoGroup.getChildren(allDescendents=True, type='geometryShape')
    geos = [x.getParent() for x in geosShape]
    return geos


def selToDict(selList, useNS):
    selDict = {}
    print 'Converting selection to Dict'

    geoGroups = pm.ls('geo_group', r=True)

    for geoGroup in geoGroups:
        ns = geoGroup.parentNamespace()
        if not ns:
            ns = 'geo_group'  # get all geometry on geo_group

        selDict[ns] = getGeoGroupMembers(geoGroup)
    print selDict
    return selDict


def getShaderFromGeo(geo):
    shapeGeo = pm.listRelatives(geo, path=True, shapes=True)
    SGGeo = pm.listConnections(shapeGeo, type='shadingEngine')
    matList = pm.listConnections(SGGeo, destination=False)
    mat = pm.ls(matList, materials=True)
    matNames = [x.name() for x in mat]
    return matNames


def getShaderFromGeoGroup(geoGroup, selList):
    if selList:
        geoList = selList
    else:
        geoList = getGeoGroupMembers(geoGroup)

    assetGeos = pm.ls(geoList, type='transform')
    shaderList = {u'lambert1'}
    assignList = {}
    for geo in assetGeos:
        shader = getShaderFromGeo(geo)
        if shader:
            assignList[str(geo.stripNamespace())] = shader[0]
            shaderList.add(shader[0])
    shaderList.discard('lambert1')
    return shaderList, assignList


def saveLook():
    print 'Saving ShadersPreset...'
    # acessa as opcoes na interface

    filePath = u'D:\JOBS\PIPELINE\pipeExemple\scenes\lookDev\preset.xml'
    path = os.path.dirname(filePath)
    base = os.path.basename(filePath)

    if base and base.find('.xml'):
        name = base.split('.')[0]
    else:
        popup('Please, choose a file name')
        return

    useNS = False
    useObjSel = False

    # verifica a selecao e se nao houver nenhuma confirma se o preset sera da cena toda.
    sel = pm.ls(sl=True, type='transform')

    if not sel:
        resp = confirmPopUp('Use the entire scene?')
        if resp == 'OK':
            selGeos = pm.ls(g=True)
            sel = pm.listRelatives(selGeos, parent=True)
        elif resp == 'Cancel':
            # return
            pass
    # converte a selecao para um selDict (dicionario com os assetSets e as geos componentes)
    selDict = selToDict(sel, True)

    print 'creating lookDict...'
    # Cria um dicionario para guardar os dados do preset (componentes, shaders, ns) considerando ou nao a selecao
    lookDict = {}
    if useObjSel:
        for ns in selDict:
            if ns == 'geo_group':
                geoGroup = pm.PyNode(ns)
            else:
                geoGroup = pm.PyNode(ns + ':geo_group')
            lookDict[ns] = getShaderFromGeoGroup(geoGroup, selDict[ns])
    else:
        for ns in selDict:
            if ns == 'geo_group':
                geoGroup = pm.PyNode(ns)
            else:
                geoGroup = pm.PyNode(ns + ':geo_group')
            lookDict[ns] = getShaderFromGeoGroup(geoGroup, '')

        print 'done.'
        print lookDict
        # saveLookPreset(path,name,lookDict)
        # saveShaders (path,name,lookDict)

        # popUp('ShadersPreset saved.')
        return lookDict


def rpbloadLook(win):
    # Acessa os parametros da interface e ferifica o nome o path do arquivo
    useNS = pm.checkBox('useNSChk', q=True, v=True)
    useObjSel = pm.checkBox('useObjSelChk', q=True, v=True)
    filePath = pm.textField('filePath_Look', q=True, text=True)
    path = os.path.dirname(filePath)
    base = os.path.basename(filePath)
    if base and base.find('.xml'):
        name = base.split('.')[0]
    else:
        popup('escolha um nome de arquivo')
        return
    # carrega o preset num dicionario
    loadedLookDict = loadLookPreset(path, name)
    # verifica a selecao e se nao houver checa se deve aplicar o preset na cena toda.
    # Se sim seleciona todas as geometrias
    sel = pm.ls(sl=True, type='transform')
    if not sel:
        resp = confirmPopUp('Aplicar o preset na cena inteira?')
        if resp == 'OK':
            selGeos = pm.ls(g=True)
            sel = pm.listRelatives(selGeos, parent=True)
        elif resp == 'Cancel':
            return
    # converte a selecao para um dicionario com assetSets e componentes.
    selDict = selToDict(sel, True)
    # chama funcao que carrega, e aplica os shaders conforme as opcoes.
    assignShaders(selDict, loadedLookDict, useNS, useObjSel, name, path)
    popUp('loading ShadersPreset done.')


def saveShaders(path, presetName, lookDict):
    # para cada assetSet no lookpreset
    for assetSet in lookDict:
        # acessa a lista de shaders
        shaderList = lookDict[assetSet][0]
        print 'saving shaders...'
        # define o nome da pasta de shaders, como o nome do asset, convertidos os ns para prefixos com '_'
        shadersPath = os.path.join(path, 'shaders', nsToPrefix(assetSet))
        # cria o diretorio se nao houver
        if not os.path.exists(shadersPath):
            os.makedirs(shadersPath)
        # grava cada shader da lista
        for shader in shaderList:
            SG = pm.listConnections(shader, type='shadingEngine')[0]
            pm.select(SG, r=True, ne=True)
            pm.file(os.path.join(shadersPath, stripNameSpace(shader) + '.ma'), op="v=0", typ="mayaAscii", es=True,
                    force=True)
        print 'shaders saved.'


def assignShaders(selDict, presetDict, useNs, useObjSel, shaderNs, shaderPath):
    print 'Assinalando SHADERs...'
    # conforme os parametros gera o nome de procura com ou sem ns
    for assetSet in selDict:
        if useNs:
            assetSetName = assetSet
        else:
            assetSetName = stripNameSpace(assetSet)
        # gera uma lista com todos os os itens no dicionario que correspondem ao nome do asset selecionado(com ns ou sem)
        assingListName = [x for x in presetDict if assetSetName in x]
        # noinspection PyNonAsciiChar
        if assingListName:
            # Se foi achado mais de um match de nome, somente o primeiro sera usado.
            # Por definicao se usarmos mais de um rig igual, devemos usar namespace para diferencia-los
            # ou o primeiro preset achado sera aplicado em todos os rigs iguais.
            if len(assingListName) > 1:
                print 'Aviso: mais q um asset achado com o mesmo base name. Pode haver erro de assignment'
            # acessa a lista de coneccao dos shaders lida no preset
            assignList = presetDict[assingListName[0]][1]
            # conforme os parametros gera a lista de geometrias
            if useObjSel:
                geoList = selDict[assetSet]
            else:
                geoList = pm.sets(assetSet, q=True)

            # gera uma lista para depois apagar os shaders antigos
            oldShadersList = {u'lambert1'}

            # para cada geometria definidas na lista, gera o nome de busca
            for geo in geoList:
                if useNs:
                    geoName = geo
                else:
                    geoName = stripNameSpace(geo)

                geoAssignName = [x for x in assignList if geoName in x]
                # Se forem achados mais de um nome de geometria igual pode haver erro de aplicacao de shader.
                # Por definicao os rigs devem ter modelos com nomes unicos
                if len(geoAssignName) > 1:
                    print 'Aviso: mais q uma geometria com o mesmo base name.Pode haver erro de assingment.'  # acessa o nome do shader

                if geoAssignName:
                    shader = assignList[geoAssignName[0]]
                else:
                    print 'Aviso: geometria nao encontrada no assignList'
                    shader = 'lambert1'
                    print 'Aviso:' + geoName + ' nao encontrada no assignList'

                # faz o assign do shader. Se ele for o default aplica o q j� esta na cena.
                if shader != 'lambert1':
                    # se o shader ainda nao existir na cena, importa.
                    if not pm.objExists(shaderNs + ':' + shader):
                        # carrega o shader. Seta o path usando o nome do asset que estava no preset.
                        shaderFullPath = os.path.join(shaderPath, 'shaders', nsToPrefix(assingListName[0]),
                                                      shader + '.ma')
                        nodeList = pm.file(shaderFullPath, i=True, ns=shaderNs, mnc=True, typ="mayaAscii", rnn=True)
                        # apaga os namespaces que existirem no node importado do shader
                        importedNS = set([])
                        for node in nodeList:
                            if node[0] == '|':
                                node = node[1:]
                            pm.rename(node, shaderNs + ':' + stripNameSpace(node))
                            nsList = getNameSpace(node)
                            importedNS.add(nsList)
                        if shaderNs in importedNS:
                            importedNS.remove(shaderNs)

                        for ins in importedNS:
                            allNsToDelete = ins.split(':')[1:]
                            for i in reversed(range(0, len(allNsToDelete))):
                                nsToDelete = ''
                                for j in range(0, i + 1):
                                    nsToDelete = nsToDelete + allNsToDelete[j] + ':'
                                nsToDel = shaderNs + ':' + nsToDelete
                                pm.namespace(rm=nsToDel)

                    # conecta o shader na geometria
                    SGList = pm.listConnections(shaderNs + ':' + shader, type='shadingEngine')
                    if SGList:
                        SG = SGList[0]
                        oldShader = getShaderFromGeo(geo)
                        pm.sets(geo, e=True, forceElement=SG)
                        # guarda a lista de shaders antigos para apagar.
                        if oldShader:
                            oldShadersList.add(oldShader[0])
                    else:
                        print 'Aviso: SG  de' + shader + ' nao encontrada. Assinalando lambert1'
                        pm.sets(geo, e=True, forceElement='initialShadingGroup')

                # se o shader for o default, assinala o default existente na cena.
                else:
                    pm.sets(geo, e=True, forceElement='initialShadingGroup')

            # apaga shaders antigos
            # sao apagados todos juntos depois para garantir que n�o serao apagados
            # shaders que estao sendo usados em outros modelos da cena
            oldShadersList.discard('lambert1')
            for shader in oldShadersList:
                SG = pm.listConnections(shader, type='shadingEngine')[0]
                geoList = pm.listConnections(SG, type='shape')
                if not (geoList):
                    try:
                        pm.delete(shader, SG)
                    except:
                        print 'nao deu pra apagar shader'

            # remove ns da importacao dos shaders
            # Varias mensagens de clash serao emitidas. Mas isso nao ser� problema.
            if pm.namespace(exists=shaderNs):
                pm.namespace(moveNamespace=[shaderNs, ':'], force=True)
                pm.namespace(removeNamespace=shaderNs)
            print 'SHADERs OK!'


def loadLookPreset(path, presetName):
    lookDict = {}
    fileName = os.path.join(path, presetName + '.xml')

    try:
        xmlFile = xml.parse(fileName)
    except:
        print 'Erro lendo XML %s' % fileName
        sys.exit('Erro lendo XML')

    xmlRoot = xmlFile.getroot()
    xmlChilds = xmlRoot.getchildren()

    for xmlAssetCntrlSet in xmlChilds:
        ref = prefixToNs(xmlAssetCntrlSet.get('ref'))

        if ref:
            ref = ref + ':'
        else:
            ref = ''

        xmlShaderList = xmlAssetCntrlSet.find('shaderList').getchildren()
        shaderList = set([])
        for xmlShader in xmlShaderList:
            shaderList.add(xmlShader.tag)

        xmlAssignList = xmlAssetCntrlSet.find('assignList').getchildren()
        assignList = {}

        for xmlAssign in xmlAssignList:
            assignList[ref + xmlAssign.tag] = xmlAssign.get('shader')
        lookDict[ref + xmlAssetCntrlSet.tag] = [shaderList, assignList]
    print 'preset loaded'
    return lookDict


def saveLookPreset(path, presetName, lookDict):
    print presetName
    print path
    print lookDict
    print 'saving preset...'
    xmlRoot = xml.Element(presetName)
    for assetCntrlSet in lookDict:
        xmlAsset = xml.SubElement(xmlRoot, stripNameSpace(assetCntrlSet))

        # descobre o namespace do assetSet
        refName = nsToPrefix(getNameSpace(assetCntrlSet))
        if not refName:
            refName = ''

        xmlAsset.attrib['ref'] = refName
        xmlShaderList = xml.SubElement(xmlAsset, 'shaderList')

        for shader in lookDict[assetCntrlSet][0]:
            xmlShader = xml.SubElement(xmlShaderList, stripNameSpace(shader))

        xmlAssignList = xml.SubElement(xmlAsset, 'assignList')
        for geo in lookDict[assetCntrlSet][1]:
            xmlGeo = xml.SubElement(xmlAssignList, stripNameSpace(geo))

            shader = stripNameSpace(lookDict[assetCntrlSet][1][geo])
            xmlGeo.attrib['shader'] = shader

            # path=os.path.join (path, presetName)
    if not os.path.exists(path):
        os.makedirs(path)

    fileName = os.path.join(path, presetName + '.xml')
    fileXML = open(fileName, 'w')
    xml.ElementTree(xmlRoot).write(fileXML)
    fileXML.close()
    print 'preset saved'
