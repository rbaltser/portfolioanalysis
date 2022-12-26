
import requests 
from datetime import datetime
from datetime import date
import os
 
# USER ACCOUNT, PORTFOLIO AND PERIOD DATA. SHOULD BE EDITED FOR YOUR NEEDS #
 
# Nordnet user account credentials and name of primary portfolio (first one listed in Nordnet)
user = ''
password = ''
primaryportfolioname = "Frie midler"
 
# Names and portfolio ids for all any all secondary portfolios. The id is listed in 
# Nordnet when selecting a portfolio. If no secondary portfolios the variable
# secondaryportfolioexists should be set to False.
secondaryportfolioexists = True
secondaryportfolios = [
{'name': 'Ratepension', 'id': ''},
]
 
# Start date (start of period for transactions) and date today used for extraction of transactions
startdate = '01.01.2013'
today = date.today()
enddate = datetime.strftime(today, '%d.%m.%Y')
 
 
# Manual date lines. These can be used if you have portfolios elsewhere that you would
# like to add manually to the data set. If no manual data the variable manualdataexists
# should be set to False
manualdataexists = True
manualdata = """
Id;Bogføringsdag;Handelsdag;Valørdag;Transaktionstype;Værdipapirer;Instrumenttyp;ISIN;Antal;Kurs;Rente;Afgifter;Beløb;Valuta;Indkøbsværdi;Resultat;Totalt antal;Saldo;Vekslingskurs;Transaktionstekst;Makuleringsdato;Verifikations-/Notanummer;Depot
;30-09-2013;30-09-2013;30-09-2013;KØBT;Obligationer 3,5%;Obligationer;;72000;;;;-69.891,54;DKK;;;;;;;;;Frie midler
"""
 
 
# CREATE OUTPUT FOLDER AND VARIABLES FOR LATER USE. #
 
# Checking that we have an output folder to save our csv file
if not os.path.exists("./output"):
    os.makedirs("./output")
 
# Creates a dictionary to use with cookies  
cookies = {}
 
# A variable to store transactions before saving to csv
transactions = ""
 
# Payload for transaction requests
payload = {
'year': 'all',
'month': 'all',
'trtyp': 'all',
'vp': 'all',
'curr': 'all',
'sorteringsordning': 'fallande',
'sortera': 'datum',
'startperiod': startdate,
'endperiod': enddate
}
 
# LOGIN TO NORDNET #
     
# First part of cookie setting prior to login
url = 'https://classic.nordnet.dk/mux/login/start.html?cmpi=start-loggain&amp;state=signin'
r = requests.get(url)
 
cookies['LOL'] = r.cookies['LOL']
cookies['TUX-COOKIE'] = r.cookies['TUX-COOKIE']
 
# Second part of cookie setting prior to login
url = 'https://classic.nordnet.dk/api/2/login/anonymous'
r = requests.post(url, cookies=cookies)
cookies['NOW'] = r.cookies['NOW']
 
# Actual login that gets us cookies required for primary account extraction
url = "https://classic.nordnet.dk/api/2/authentication/basic/login"
 
r = requests.post(url,cookies=cookies, data = {'username': user, 'password': password})
 
cookies['NOW'] = r.cookies['NOW']
cookies['xsrf'] = r.cookies['xsrf']
 
 
# GET PRIMARY ACCOUNT TRANSACTION DATA #
 
# Get CSV for primary account
url = "https://classic.nordnet.dk/mux/laddaner/transaktionsfil.html"
data = requests.get(url, params=payload, cookies=cookies)
result = data.text
result = result.splitlines()
firstline = 0
 
for line in result:
    if line and firstline == 0:
        transactions += line + ';' + "Depot" + "\n"
        firstline = 1
    elif line:
        # Sometimes Nordnet inserts one semicolon too many in the file. This removes the additional semicolon
        if line.count(';') == 22:
            position = line.rfind(';')
            line = line [:position] + line[position+1:]
        transactions += line + ';' + primaryportfolioname + "\n"
 
         
# GET TRANSACTION DATA FOR ALL/ANY SECONDARY ACCOUNTS #
 
if secondaryportfolioexists == True:
    for item in secondaryportfolios:
        # Switch to secondary account and set new cookies
        url = 'https://classic.nordnet.dk/mux/ajax/session/bytdepa.html'
        headers = {'X-XSRF-TOKEN': cookies['xsrf']} 
         
        r = requests.post(url,cookies=cookies, headers=headers, data = {'portfolio': item['id']})
 
        cookies['NOW'] = r.cookies['NOW']
        cookies['xsrf'] = r.cookies['xsrf']
 
        # Get CSV for secondary account
        url = "https://classic.nordnet.dk/mux/laddaner/transaktionsfil.html"
        data = requests.get(url, params=payload, cookies=cookies)
        result = data.text
        result = result.split("\n",1)[1]
        result = result.splitlines()
 
        for line in result:
            if line:
                # Sometimes Nordnet inserts one semicolon too many in the file. This removes the additional semicolon
                if line.count(';') == 22:
                    position = line.rfind(';')
                    line = line [:position] + line[position+1:]
                transactions += line + ';' + item['name'] + "\n"
 
 
if manualdataexists == True:
    manualdata = manualdata.split("\n",2)[2]
    transactions += manualdata              
 
 
# WRITE CSV OUTPUT TO FILE #
         
with open("./output/trans.csv", "w", encoding='utf8') as fout:
    fout.write(transactions)</p></pre>