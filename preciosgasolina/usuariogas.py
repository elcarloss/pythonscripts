#! /home/calarcon/pyvirtual/bin/python

from geojson import Feature, Point, FeatureCollection
import json
import geojson
import xml.etree.ElementTree as ET 
import geopy.distance
import operator
import arrow

def validarpunto(puntos):
    if (puntos[0] > 200 or puntos[1] > 200):
        puntos = (0,0)
    else:
        if (puntos[0] < 0):
            puntos = (puntos[1], puntos[0])
        if (puntos[0] > 0 and puntos[1] > 0):
            puntos = (puntos[1], puntos[0])
        if puntos[1] > 0:
            puntos = (puntos[0], '-' + str(puntos[1]))
            puntos = (puntos[0], float(puntos[1]))
    return puntos

geometry = []
props = []
imagen = 'icogas.png'
usuario = (21.92934, -102.33915)
listadict = []
listamypoint = []
featurecollection = []
listafeat=[] 
treeplaces = ET.parse('places') 
rootplaces = treeplaces.getroot() 
treeprices = ET.parse('prices') 
rootprices = treeprices.getroot() 
datos = [] 
cont = 0  
cont2 = 0
con = 1
x = 0  
nombre = '' 
icoverde = {"image" : "icogasverde.png"}
icorojo = {"image" : "icogasrojo.png"}
print("Ejecutando .....") 
for child in rootplaces:  
    ide = child.attrib['place_id']   
    for nietos in child:  
        cont = cont + 1  
#        y = 0  
#        y = y + 1  
        if nietos.tag == 'name':  
            nombre = nietos.text  
        if nietos.tag == "location":  
            x = 0  
            for element in nietos:  
                x = x + 1  
                if x == 2:  
                    lon = element.text  
                if x == 3:  
                    lat = element.text  
            tup = (float(lon), float(lat))
            tupgeopy = validarpunto(tup)
            if ((geopy.distance.distance(usuario, tupgeopy).km) <= 4): 
                tupgeopyexp = (tupgeopy[1], tupgeopy[0])
                for prices in rootprices.findall("./place/[@place_id='%s']" % ide):     
                    precios = []
                    for datos in prices:   
                        precios.append(datos.get('type'))   
                        precios.append(datos.text)  
                        precios.append(datos.get('update_time'))  			    
                    if precios:
                        mypoint = Point(tupgeopyexp)
                        if not "diesel" in precios[0]:
                            if  len(precios) == 6: 
                                propiedades = {'description':  precios[0]+': '+precios[1]+', '+precios[3]+': '+precios[4]+' - Actualizado el '+precios[2], 'title' : nombre, 'image': imagen, 'point' : mypoint}
                            else:
                                propiedades = {'description':  precios[0]+': '+precios[1]+' - Actualizado el '+precios[2], 'title' : nombre, 'image': imagen, 'point' : mypoint}
                            listadict.append(propiedades)
listadict.sort(key=operator.itemgetter('description'))
print("Lista Ordenada: ",listadict)
for x in listadict:
    puntos = x['point']
    print("Puntos: ", puntos)
    x.pop('point')
    cadaux = listadict[cont2]['description']
    prec, fechag = cadaux.split("el ")
    hoy = arrow.now()
    fechagas = arrow.get(fechag)
    antiguedad = hoy - fechagas
#    print("Solo Fecha: ", fechagas)
    print("Antiguedad: ", antiguedad)
    antistr = str(antiguedad)
    antig = antistr.split(" ")[0]
#    print(type(antistr))
    print("Antiguedad String: ", antistr)
#    print("Cont2: ", cont2)
#    print("Long de listadict: ", len(listadict))
    print("listadict[cont2]: ", listadict[cont2]['description'])
    if not(",") in antistr:
       antig = "0"
    if 'regular' in listadict[cont2]['description'] and con == 1 and int(antig) < 3:
        print("ENTRO GASOLINA BARATA!!!!!!!!!")
        listadict[cont2].update(icoverde)
        con = 2
    print("Cont2: ", cont2)
    if 'regular' in listadict[cont2]['description'] and int(antig) < 5 and len(listadict) == (cont2+1):
        print("ENTRO A LA GASOLINA MAS CARA!!!!")
        listadict[cont2].update(icorojo)
    feature = Feature(geometry=puntos, properties=x)
    featurecollection.append(feature)
    cont2 = cont2 + 1
geojson_file = FeatureCollection(featurecollection)
print("Escribiendo archivo")
f=open('nuevoarchivo.json','w')                                                                                                             
json.dump(geojson_file, f)                                                                                                                   
f.close()        
