# rsdb
my interface to db with some scanning results

24.01.2019

IP networks for scanning should be listed in file iplist.txt in current directory
IP networks can be listed in CIDR notation or like IP ranges
No nmap style...
So this is properly:
192.168.0.5
10.10.0.0/16
176.24.0.0-176.34.255.255
and this is wrong:
192.168.0.*
10.10.12-7.1
