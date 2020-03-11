import boto3
import time
import os
import sys

def get_ec2_con_for_give_region(my_region):
    ec2_con_re=boto3.resource('ec2',region_name=my_region)
    return ec2_con_re
    
def list_instances_on_my_region(ec2_con_re):
    for each in ec2_con_re.instances.all():
        print(each.id)
        
def get_instant_state(ec2_con_re, in_id):
    for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id', "Values": [in_id]}]):
        pr_st=each.state['Name']            
    return pr_st

def start_instance(ec2_con_re, in_id):
    pr_st = get_instant_state(ec2_con_re, in_id)
    if pr_st == "running":
        print("La instancia ya esta corriendo")
    else:
        for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id',"Values": [in_id]}]):
            each.start()
            print("Favor de esperar a que se inicie la instancia, cuando esto suceda se le avisara")
            each.wait_until_running()
            print("Ya se ha detenido")


def stop_instance(ec2_con_re, in_id):
    pr_st = get_instant_state(ec2_con_re, in_id)
    if pr_st == "stopped":
        print("La instancia ya esta detenida")
    else:
        print("Aqui truena")
        for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id',"Values": [in_id]}]):
            each.stop()
            print("Favor de esperar a que se detenga la instancia, cuando esto suceda se le avisara")
            each.wait_until_stopped()
            print("Ya se ha detenido")


def create_new_instance(image_id):
    client = boto3.client('ec2')
    resp = client.run_instances(ImageId=image_id,InstanceType='t2.micro', MinCount=1, MaxCount=1, KeyName="MiawsPem")
    print("Creating a new instance")					
#    for instance in resp['Instances']:
#        print(instance['InstanceId']



def welcome():
    print("Este script te ayuda a iniciar o detener instancias ec2 basadas en la region o instancia id y a crear instances ec2")
    time.sleep(2)

def main():
    welcome()
    option = input("Type 'new' to create a new instance or 'restart' to stop or start an existing instance: ")
    if option == "restart":
        myregion = input("Enter your region name:")
        print("please wait... connecting to your aws ec2 console....")
        ec2_con_re = get_ec2_con_for_give_region(myregion)
        print("Please wait listing all instances ids in your region {}".format(myregion))
        list_instances_on_my_region(ec2_con_re)
        in_id = input("Now choose your instance id to start or stop:")
        start_sotp = input("Enter either stop or start command for your ec2 instance:")
        while True:
            if start_sotp not in ["start", "stop"]:
                start_sotp = input("Enter only stop start commands:")
                continue
            else:
                break
    else: 
        if option == "new":
            image_id = input("Please write the ami image id (This new ec2 instance will be created as t2.micro instance type) and number of instances to create:")
            create_new_instance(image_id)
            print("Creating instance based in the us-east-2 region")
            break
    if start_sotp == "start":
        print("Starting :", in_id)
        start_instance(ec2_con_re, in_id)
    else:    
        print("Stopping :", in_id)
        stop_instance(ec2_con_re, in_id)
        

if __name__ == '__main__':
    os.system('clear')
    main()
