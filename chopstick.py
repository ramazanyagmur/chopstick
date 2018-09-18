# chopstick.py Parser for cfgmml format
# It is aimed for parsing cfgmml files to be converted to a column based format. 
# It needs a default file "infiledef.txt" for output to be configured and standardized for multiple input files. 
# And will need a prewrite filler file "inprefill.txt" to make extra column on an MOC based on another MOC. 
# Then will read all files in in/ directory and output to out\ directory.
# 
# Project start date : June 2018  , Ramazan YAGMUR <ramazan.yagmur@gmail.com>
# 
# Licensed under BSD 3-Clause "New" or "Revised" License

import glob

# Checks for comments , lines starting with / (slash) are comments.
def lineisvalid(line):
	result=1
	if line[0:2]=="//": result=0
	return result

# Gets MOC of the line , MOC for  ADD UCELLSETUP: would be ADDUCELLSETUP
def linegetmoc(line):
	linesplit=line.split(":")
	linemoc=linesplit[0]
	linemoc=linemoc.replace(" ","")
	linemoc.strip()
	return linemoc

# Strip the line ends from ; (semicolon)
def linestrip(line):
	linesplit=line[0:-2].split(":")
	if len(linesplit)>=2:
		linestr=linesplit[1]
	else:
		linestr=linesplit[0]
	return linestr

# Returns parameters as list	CELLID=1234,CELLNAME="TEST11" --> [CELLID=1234,CELLNAME="TEST11"]
def linetoparamcouple(line):
	paramcouple=linestrip(line).split(",")
	return paramcouple

# Gets the line and converts to dictionary list     CELLID=1234,CELLNAME="TEST11" --> [{CELLID,1234},{CELLNAME,TEST11}]
def linetoparamval(line):
	paramcouple=linetoparamcouple(line)
	ps={}
	for pvs in paramcouple :
		pv = pvs.split("=")
		par=pv[0].strip()
		if len(pv)>=2 :
			val=pv[1].replace("\"","").strip()
		else:
			val=""
		p={}
		p[par]=val
		ps.update(p)
	return ps

# Process every line and create a list of MOC dictionary lists  
def rawdatatomoc(rawdata):
	mocold=""
	params={}
	for line in rawdata:
		if lineisvalid(line):
			moc=linegetmoc(line)
			prms=[]
			prms.append(linetoparamval(line))
			if moc in params:
				params[moc].append(linetoparamval(line))
			else:
				params[moc]=prms
	return params

# Write MOC titles to MOC output files	
def titlestofile(paramsdef):
	for mocdef, prmsdef in paramsdef.items():
		file=open("out\\" + mocdef + ".txt","w")
		# write titles
		for key,val in prmsdef[0].items():
			file.write(key+"\t")
		file.write("\n")
		file.close

# Print out all MOC params to output files		
def paramstofile(paramsdef,params):
	for mocdef, prmsdef in paramsdef.items():
		file=open("out\\" + mocdef + ".txt","a")

		#write values
		for p1 in paramsdef[mocdef]:
			try:
				for i in range(len(params[mocdef])):
					for key,val in p1.items():
						try:
							val2=params[mocdef][i][key]
						except:
							val2=""
						file.write(val2+"\t")
					file.write("\n")
			except:
				pass
		file.close

# Adds BSCNAME dict to all MOC lists , and to every line
def addbscname(params):
	pbsc={}
	pbsc["BSCNAME"]=params["SETSYS"][0]["SYSOBJECTID"]
	for moc in params :
		for p1 in params[moc]:
			p1.update(pbsc)

# Function for adding a new dict list to an MOC
def addcol(params,moc,col,val):
	pcol={}
	try:
		pcol["YES"]="YES"
		for p1 in params[moc]:
			p1.update(pcol)
	except:
		pass

# Function for updating values for an MOC column from another MOC based on matching 2 other columns		
def updatecol(params,moc,targetcol,targetref1,targetref2,refmoc,refcol1,refcol2,refresult):
	cin={}
	try:
		for p1 in params[moc]:
			t1=p1[targetref1]
			t2=p1[targetref2]
			for cell in params[refmoc]:
				if cell[refcol1]==t1 and cell[refcol2]==t2 :
					if refresult=="1":
						cin[targetcol]="1"
					else:
						cin[targetcol]=cell[refresult]	
					p1.update(cin)
	except:
		pass

# Create a ADDUCELLPARAM MOC with the inclusion of lists from ADDUCELLSETUP
def createcellparam3g(params):
	try:
		params["ADDUCELLPARAM"]=[]
		for p1 in params["ADDUCELLSETUP"]:
			cell={}
			cell["BSCNAME"]=p1["BSCNAME"]
			cell["CELLID"]=p1["CELLID"]
			cell["CELLNAME"]=p1["CELLNAME"]
			params["ADDUCELLPARAM"].append(cell)
	except:
		pass
		
# Create a ADDGCELLPARAM MOC with the inclusion of lists from ADDGCELL
def createcellparam2g(params):
	try:
		params["ADDGCELLPARAM"]=[]
		for p1 in params["ADDGCELL"]:
			cell={}
			cell["BSCNAME"]=p1["BSCNAME"]
			cell["CELLID"]=p1["CELLID"]
			cell["CELLNAME"]=p1["CELLNAME"]
			params["ADDGCELLPARAM"].append(cell)
	except:
		pass
		
# MainApp

#Read Definition Config
file=open("infiledef.txt","r")
rawdata=file.readlines()
file.close
paramsdef=rawdatatomoc(rawdata)
titlestofile(paramsdef)

#Read PreFill Config
filepf=open("inprefill.txt","r")
pfs=filepf.readlines()
filepf.close

#Get file list of "in" folder
mylist = [f for f in glob.glob("in\*.txt")]

for file1 in mylist:

	print("Processing",file1)

	#Read CFGMML file
	file=open(file1,"r")
	rawdata=file.readlines()
	file.close
	params=rawdatatomoc(rawdata)
	
	#Further proccess
	addbscname(params)
	addcol(params,"ADDGCELL","YES","YES")
	createcellparam2g(params)
	createcellparam3g(params)
	
	#Proccess PreFill Conditions
	for pf1 in pfs:
		pf = pf1.split(",")
		updatecol(params,pf[0],pf[1],pf[2],pf[3],pf[4],pf[5],pf[6],pf[7])

	#Write results to files in "out" folder
	paramstofile(paramsdef,params)

# EndOf MainApp
