#! /home/ubuntu/pyvirtual/bin/python

from geojson import Feature, Point, FeatureCollection
from flask import Flask
import json
import geojson
import xml.etree.ElementTree as ET
import geopy.distance
import operator
import arrow

app = Flask(__name__)

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



@app.route('/puntos/<name>')
def procesar_puntos(name):
    usuario = str(name)
    lati,lon = usuario.split(",")
    nombrearchivo = '/var/www/html/gas'+lati+', '+lon+'.json'
    print(type(name))
    print(nombrearchivo)
    imagen = 'icogas.png'
    featurecollection = []
    listafeat=[]
    listadict = []
    treeplaces = ET.parse('places')
    rootplaces = treeplaces.getroot()
    treeprices = ET.parse('prices')
    rootprices = treeprices.getroot()
    datos = []
    lisaux = []
    cont = 0
    cont2 = 0
    con = 1
    x = 0
    nombre = ''
    icoverde = {"image":"icogasverde.png"}
    icorojo = {"image":"icogasrojo.png"}
    print("Ejecutando .....")
    for child in rootplaces:
        ide = child.attrib['place_id']
        for nietos in child:
            cont = cont + 1  
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
                            if  len(precios) == 6:
                                propiedades = {'description':  precios[0]+': '+precios[1]+', '+precios[3]+': '+precios[4]+' - Actualizado el '+precios[2], 'title' : nombre, 'image': imagen, 'point' : mypoint}
                            else:
                                propiedades = {'description':  precios[0]+': '+precios[1]+' - Actualizado el '+precios[2], 'title' : nombre, 'image': imagen, 'point' : mypoint}
                        listadict.append(propiedades)
    listadict.sort(key=operator.itemgetter('description'))
    for x in listadict:
        puntos = x['point']
        x.pop('point')
        cadaux = listadict[cont2]['description']
        print("Solo Descripción: ", cadaux)
        prec, fechag = cadaux.split("el ")    
        fechagas = arrow.get(fechag)
        hoy = arrow.now()
        antiguedad = hoy - fechagas
        antistr = str(antiguedad)
        antig = antistr.split(" ")[0]
        print("Antiguedad Str: ", antiguedadstr)
        if 'regular' in listadict[cont2]['description'] and con == 1 and int(antig) < 5:
            listadict[cont2].update(icoverde)
            con = 2
        feature = Feature(geometry=puntos, properties=x)
        featurecollection.append(feature)
        cont2 = cont2 + 1
        if 'regular' in listadict[cont2]['description'] and int(antig) < 5 and len(listadict) == (cont2+1):
            listadict[cont2].update(icorojo)
    geojson_file = FeatureCollection(featurecollection)
    print("Escribiendo archivo")
    lati = lati.replace(".", "_")
    archivo = "/var/www/html/"+lati+".json"
    f=open(archivo,'w')
    json.dump(geojson_file, f)
    f.close()
    salida = "Archivo escrito correctamente: "+archivo
    return salida

if __name__ == '__main__':
    app.run(host='172.31.26.21', port=8080)
