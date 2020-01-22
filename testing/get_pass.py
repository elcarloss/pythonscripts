#!/usr/bin/python2.7

import getpass

p = getpass.getpass(prompt='Your favorite flower? ') 
if p.lower() == 'rose': 
    print('Welcome..!!!') 
else: 
    print('The answer entered by you is incorrect..!!!') 

