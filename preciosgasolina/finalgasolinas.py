from geojson import Feature, Point, FeatureCollection
import json
import geojson
import xml.etree.ElementTree as ET 
featurecollection = []
listafeat=[] 
treeplaces = ET.parse('places') 
rootplaces = treeplaces.getroot() 
#treeprices = ET.parse('prices') 
#rootprices = treeprices.getroot() 
datos = [] 
cont = 0  
x = 0  
nombre = ''  
for child in rootplaces:  
    ide = child.attrib['place_id']   
    for nietos in child:  
        cont = cont + 1  
        y = 0  
        y = y + 1  
        if nietos.tag == 'name':  
            nombre = nietos.text  
#        precios = []     
#        for prices in rootprices.findall("./place/[@place_id = '%s']" % lugar):     
#            for datos in prices:   
#                if y < 2: 
#                    precios.append(datos.get('type'))   
#                    precios.append(datos.text)  
#                    precios.append(datos.get('update_time'))  
        if nietos.tag == "location":  
            x = 0  
            for element in nietos:  
#                print element.text  
                x = x + 1  
                if x == 2:  
                    lon = element.text  
                if x == 3:  
                    lat = element.text  
            tup = (float(lon), float(lat))
    mypoint = Point(tup)   
    propiedades = {'Nombre': nombre}   
    print(mypoint)
#    listafeat.append("Feature%s(geometry=%s, properties=%s})" % (ide, mypoint, properties))
    feature = Feature(geometry=mypoint, properties=propiedades)
    featurecollection.append(feature)

    f = open('1erjson.json', 'w')                                                                                                                
    json.dump(geojson_file, f)                                                                                                                   
    f.close()        

print(feature)
geojson_file = FeatureCollection(featurecollection)
#     print("Nombre :", nombre)  
#     datos.append(lat)
#     datos.append(lon)
#     datos.append(lugar)
#     print("Latitud :", lat)                
#     print("Longitud :", lon)  
#     print("ID: ", ide)  
#     print(mypoint)
#print(listafeat)
#     print("Precios: ", precios)  
#     print("\n")


from geojson import Feature, Poin
import xml.etree.ElementTree as ET 
  
 treeplaces = ET.parse('places') 
 rootplaces = treeplaces.getroot() 
 treeprices = ET.parse('prices') 
 rootprices = treeprices.getroot() 
  
 cont = 0  
 x = 0  
 nombre = ''  
 for child in rootplaces:  
     lugar = child.attrib['place_id']   
     for nietos in child:  
         cont = cont + 1  
         y = 0  
         y = y + 1  
         if nietos.tag == 'name':  
             nombre = nietos.text  
         precios = []     
         for prices in rootprices.findall("./place/[@place_id = '%s']" % lugar):     
             for datos in prices:   
                 if y < 2: 
                     precios.append(datos.get('type'))   
                     precios.append(datos.text)  
                     precios.append(datos.get('update_time'))  
         if nietos.tag == "location":  
             x = 0  
             for element in nietos:  
 #                print element.text  
                 x = x + 1  
                 if x == 2:  
                     lon = element.text  
                 if x == 3:  
                     lat = element.text  
     print("Nombre :", nombre)  
     print("Latitud :", lat)                
     print("Longitud :", lon)  
     print("Lugar: ", lugar)  
     print("Precios: ", precios)  
     print("\n") 

