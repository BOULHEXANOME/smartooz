import json
from pprint import pprint
import requests

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
        
        
def add_places():
    target = 'http://142.4.215.20:1723'
    resp = {
        'status': 'KO'
    }
    with open('Row1.json') as data_file:
        dataFile = json.load(data_file)
    x = -1
    listErrors = []
    nbErrors = 0
    
    #Register if not already done
    pprint("-----Register a user to enter the database-----")
    url = target + "/register"
    data = {'password': 'hugo', 'username': 'hugo', 'email': 'hugoemail'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    z = json.loads(r.text)
    if z['status'] == 'KO':
        print('Failure...')
    else:
        print('Success !')
        
    pprint("-----Login the user-----")
    #Login
    url2 = target + "/login"
    data2 = {'password': 'hugo', 'username': 'hugo'}
    headers2 = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r2 = requests.post(url2, data=json.dumps(data2), headers=headers2)
    cookies = r2.cookies
    z = json.loads(r2.text)
    if z['status'] == 'KO':
        print('Failure...')
    else:
        print('Success !')
    
    pprint("-----And finally : try to add data-----")
    '''url3 = "/add-place"
    data3 = {'latitude': '45.631', 'longitude': '4.888', 'address':'ta mere', 'openning_hours':'oui', 'name':'truc', 'description':'non', 'keywords':['truc','machin']}
    headers3 = {'Content-type': 'application/json'}
    r3 = requests.post(url3, cookies=cookies, data=json.dumps(data3), headers=headers3)
    pprint(r3.text)'''
    while True:
        x = x + 1
        try: 
            pprint("Inserting Object Number : " + str(x))
            y = dataFile[str(x)]["id"]
        except:
            break
            
        try:
            lat = dataFile[str(x)]["latitude"]
        except:
            lat = "null"
        try:
            long = dataFile[str(x)]["longitude"]
        except:
            long = "null"
        try:
            adr = dataFile[str(x)]["address"]
        except:
            adr = "null"
        try:
            ope = dataFile[str(x)]["openning_hours"]
        except:
            ope = "null"
        try:
            nam = dataFile[str(x)]["name"]
        except:
            nam = "sansNom"+str(x)
        try:
             des = dataFile[str(x)]["description"]
        except:
             des = "rien a afficher"
        keys = ['Lyon']
        try:
            keys1 = dataFile[str(x)]["type_detail"]
            keys.append(keys1)
        except:
            keys1 = []
        try:
            keys2 = dataFile[str(x)]["commune"]
            keys.append(keys2)
        except:
            keys2 = []
        try:  
            #Add new data
            url3 = target + "/add-place"
            data3 = {'latitude': lat, 'longitude': long, 'address':adr, 'openning_hours':ope, 'name':nam,'description':des,'keywords':keys}
            headers3 = {'Content-type': 'application/json'}
            r3 = requests.post(url3, cookies=cookies, data=json.dumps(data3), headers=headers3)
            z = json.loads(r3.text)
            if z['status'] == 'KO':
                listErrors.append(x) 
                nbErrors = nbErrors + 1
                print(z)
            
        except:
                print('ERROR : something very bad happened...')
                print('Exiting treatment')
                break
    pprint('-----The following objects were not inserted : -----')
    print(listErrors)
    print('-----Success rate : -----')
    print(str(100 - nbErrors*100/x)+'%')
    return 0
    
add_places()
