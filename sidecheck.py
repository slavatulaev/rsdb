#!/usr/bin/python3.5

# -*- coding: UTF-8 -*-
# enable debugging
import cgitb, sys, cgi

########## vars ########
cgitb.enable()    

f = open('list')
ips = []
for l in f:
	ips.append(l.strip())
f.close()

print("Content-Type: text/html;charset=utf-8")
print()    

########################

form = cgi.FieldStorage()

if "IP" not in form:
	print('Input IP:')
else:
	varIP = form['IP'].value.strip()
	if varIP in ips:
		print(varIP + 'already been found and sold')
	else:
		print(varIP + 'never been found before')
	print('\n\nInput IP:')

########################


print('<form action="t.py" method="post">')
print('<input type="text" name="IP" placeholder="IP">') 
print('<input type="submit" value="Submit">')
print('</form>')

