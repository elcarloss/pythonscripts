import logging
import pif
from godaddypy import Client, Account


logging.basicConfig(filename='godaddy.log', format='%(asctime)s %(message)s', level=logging.INFO)

my_acct = Account(api_key='e52xSqLBxqDf_6LNm7ZQzA2gZtPioxPkynu', api_secret='GqwcELGWrvChmkf83XtNan')
client = Client(my_acct)
public_ip = pif.get_public_ip('v4.ident.me')


for dominio in client.get_domains():
    records = client.get_records(dominio, record_type='A') 
    logging.debug("Dominio '{0}' Registros DNS: {1}".format(dominio, records[0]['data']))
    actual_ip = records[0]['data']
    if public_ip != records[0]['data']:
        client.update_ip(public_ip, domains=dominio)
        client.update_record_ip(public_ip, dominio, 'dynamic', 'A')
        logging.info("Dominio '{0}' Ip Pública configurada a '{1}'".format(dominio, public_ip))    


actual = client.get_records(dominio, record_type='A')
print("Configuración Final:")
print(actual)

