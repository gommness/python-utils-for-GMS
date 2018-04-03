"Wellcome to the tileReplacer help!\
\nthis tool uses a simple language to perform replacements on the tiles of your rooms!\
\n\
\nyou can call this script as follows:\
\n\
\n   python tileReplacer.py\
\n   this will start the user prompt, where you can write the replacements or other commands.\
\n\
\n   python tileReplacer.py -f scriptFile\
\n   this will try to read the replacement statements from the file scriptFile.\
\n\
\n   python tileReplacer.py <statemetns>\
\n   this will execute the statement passed as argument.\
\n\
\nthe language goes as follows:\n\
\n   in rooms/room0.room.gmx\
\n      declares that the replacement will take place in room0\
\n   replace background/tileSet0.background.gmx\
\n      declares tileSet0 as the tileset whose tiles will be replaced\
\n   with background/tileSet1.background.gmx\
\n      declares tileSet1 as the tileset whose tiles will replace the other tiles\
\n   tiles (0,0)<(1,1)\
\n      replaces tile at the position (0,0) from tileSet0 with the tile at the position (1,1) from tileSet1\
\nline breaks do not matter (as long as they don't split a word)\
\nplease note that the syntax of the 'tiles' part is a bit strict:\
\nNo extra spaces, characters nor line breaks there are allowed\
\n\
\nYou can make more complex operations by concatenating simpler ones:\
\nin room0 replace ts_house with ts_cave tiles (0,0)<(0,0) (0,2)<(1,2)\
\nwith ts_aux tiles (0,1)<(0,1) in room1 tiles (0,0)<(0,0)\
\n\
\nthere is also some special commands you can input:\n\
\n   HELP\
\n      displays this information. note that this command cannot be interpreted correctly within\
\n      a statement, only as a prompt command\
\n\nthe next ones also can be anywhere in a statement\n\
\n   ABORT\
\n      this will end the prompt interpreter.\
\n   EXIT and QUIT\
\n      same as ABORT\
\n   SET ROOMFOLDER {path to the room folder}\
\n      this tells the program where to look for room files (so you don't have to input the whole path)\
\n   SET BACKGROUNDFOLDER {path to the background folder}\
\n      this tells the program where to look for background files (so you don't have to input the whole path)\
\n   SET ABBREVIATION {1, 0}\
\n      1 means that the program will work out the default file extensions by itself. 0 means it won't (default is 1)\
\n      this way you don't have to input the whole .something.gmx when telling the program the name of the file\
\n   UNSET ROOMFOLDER, UNSET BACKGROUNDFOLDER, UNSET ABBREVIATION: these will return those to its default values\
\n   PRINT ROOMFOLDER, PRINT BACKGROUNDFOLDER, PRINT ABBREVIATION\
\n      these will print out the values of those variables\
\n\
\nI hope this is enough to illustrate how this tool works. For more reference, please check the example files."
"""
TODO:
	documentar algunas funciones
	documentar clase TileSet
	mejorar documentacion del modulo
	pruebas del sistema
	comentar codigo en general
"""
"""\
\nthe string follows the next syntax:\
\
\nAXIOM ::= STR AXIOM\
\nAXIOM ::= \
\nSTR ::= ROOM FROM REPLACE tiles PAIRS\
\nSTR ::= ROOM REPLACE FROM tiles PAIRS\
\nSTR ::= REPLACE ROOM FROM tiles PAIRS\
\nSTR ::= REPLACE FROM ROOM tiles PAIRS\
\nSTR ::= FROM REPLACE ROOM tiles PAIRS\
\nSTR ::= FROM ROOM REPLACE tiles PAIRS\
\nROOM ::= \
\nFROM ::= with TS\
\nFROM ::= \
\nREPLACE ::= replace TS\
\nREPLACE ::= \
\nPAIRS ::= PAIR\
\nPAIRS ::= PAIRPAIRS\
\nPAIR ::= (INT,INT)<(INT,INT)\
\n\
\nINT ::= {positive integer number}\
\nTS ::= {path of a tileSet}\
\nROOM ::= in {path of a room}\n\
\
\nif DECLARATION is missing, the program will check for the lasts ts_src and ts_dst refered to\
\nif ROOM is missing, the program will check for the last room refered to\
\nif FROM is missing, the program will check for the last ts_src refered to\
\nif REPLACE is missing, the program will check for the last ts_dst refered to\
\nSpaces are not allowed on any PAIR (pls understand, this makes things easier for me)\
\
\n\nExample of a well constructed statement:\
\nin room0 replace ts_house with ts_mountain tiles (2,1)<(0,0) (0,1)<(2,2) with ts_village tiles (0,2)<(0,1).\
\nthis will, in room0, replace ts_house\'s (2,1) and (0,1) with ts_mountain\'s (0,0) and (2,2). And ts_house\'s (0,2) with ts_village\'s (0,1)\
\n\
"""



print "\nthanks for using this script!"
print "author's twitter: @gommness   come by and say hi!"
import xml.etree.ElementTree as ET
import sys
import os
import re

class CustomException(Exception):
	pass

ts_registry = {}
room_registry = {}
roomFolder = ""
backgroundFolder = ""
abbreviation = 1
ts_src=None
ts_dst=None
room = None
reserved=["in","replace","with","tiles","set","unset","print"]
quitWords=["abort","exit","quit"]
special=["roomFolder","backgroundFolder", "abbreviation"]
execStack=[]

def help():
	print __doc__+"\n"


class tileSet():
	def __init__(self, ts_name):
		try:
			tree=ET.parse(ts_name)
			root=tree.getroot()
			if not root.tag == "background":
				raise CustomException("file '"+ts_name+"' is not a background file")
			if not (root.findall('istileset')[0].text == "-1"):
				raise CustomException("background '"+ts_name+"' is not a tileSet")
			self.tileWidth = int(root.findall('tilewidth')[0].text)
			self.tileHeight = int(root.findall('tileheight')[0].text)
			self.xOff = int(root.findall('tilexoff')[0].text)
			self.yOff = int(root.findall('tileyoff')[0].text)
			self.hSep = int(root.findall('tilehsep')[0].text)
			self.vSep = int(root.findall('tilevsep')[0].text)
			self.xSize = (int(root.findall('width')[0].text)-self.xOff)/(self.tileWidth+self.hSep)
			self.ySize = (int(root.findall('height')[0].text)-self.yOff)/(self.tileHeight+self.vSep)
			self.name = ts_name
		except CustomException as inst:
			raise inst
	def withinLimits(self,x,y):
		return (x >= self.xSize or y >= self.ySize)
	def posToCoord(px,py):
		cx = self.xOff+px*self.tileWidth
		cy = self.yOff+py*self.tileHeight
		return (cx,cy)
	def coordToPos(cx,cy):
		px = (cx-self.xOff)/(self.tileWidth+self.hSep)
		py = (cy-self.yOff)/(self.tileHeight+self.vSep)
		return (px,py)

def customPrint(s):
	print s

def clear():
	'clears all variables related to the execution stack'
	global ts_src, ts_dst, room, execStack, ts_registry, room_registry
	ts_src=None
	ts_dst=None
	room=None
	for t in execStack:
		del t
	execStack=[]
	ts_registry = {}
	room_registry = {}

def cleanExecution():
	global execStack, ts_registry, room_registry
	for t in execStack:
		del t
	execStack=[]
	ts_registry = {}
	room_registry = {}

def collapse(str,s):
	'if the substring s repeats within str, collapses them into a single one s'
	return re.sub(s+"+",s,str)

def isEnd(s):
	'checks whether s is the end of the axiom or not'
	return s[-1] == '.'

def isReserved(s):
	'checks whether s is a reserved word'
	global reserved
	return s.lower() in map(str.lower, reserved)

def isSpecial(s):
	'checks whether s is a special word'
	global special
	return s.lower() in map(str.lower, special)

def isQuitWord(s):
	'checks whether s is a reserved word'
	global quitWords
	return s.lower() in map(str.lower, quitWords)

def setRoomFolder(s):
	global roomFolder
	'sets the room folder so that it auto completes when finding a room file'
	roomFolder=s

def setBackgroundFolder(s):
	global backgroundFolder
	'sets the background folder so that it auto completes when finding a background file'
	backgroundFolder=s

def setAbbreviation(n):
	global abbreviation
	'sets the flag that tells the program when to autocomplete file extensions'
	abbreviation=n

def unset(s):
	global roomFolder, backgroundFolder, abbreviation
	if s.lower == "roomFolder":
		roomFolder = ""
	elif s.lower == "backgroundFolder":
		backgroundFolder = ""
	elif s.lower == "abbreviation":
		abbreviation = 1
	else:
		print "warning. unknown unset variable "+s

def prepareFileName(s,typ):
	'using the abbreviaton variables as well as the folder names, returns the prepared name of the file'
	global backgroundFolder, roomFolder, abbreviation
	if abbreviation == 1:
		s = s.split(".")[0]+"."+typ+".gmx"
	if typ == "room":
		s = os.path.join(roomFolder,s)
	else:
		s = os.path.join(backgroundFolder,s)
	return s

def loadSrc(s):
	"loads the ts_src from the filename s"
	global ts_registry, ts_src
	if s in ts_registry:
		ts_src = ts_registry[s]
	else:
		ts_src = tileSet(s)
		ts_registry[s] = ts_src

def loadDst(s):
	'loads the ts_dst from the filename s'
	global ts_registry, ts_dst
	if s in ts_registry:
		ts_dst = ts_registry[s]
	else:
		ts_dst = tileSet(s)
		ts_registry[s] = ts_dst

def loadRoom(s):
	'loads the room from the filename s'
	global room_registry, room
	if s in room_registry:
		room = room_registry[s]
	else:
		try:
			room = ET.parse(s)
			if not room.getroot().tag == "room":
				raise CustomException("file '"+ts_name+"' is not a room file")
			room_registry[s] = room
		except CustomException as inst:
			raise inst

def parseTiles(s):
	'given a string containing the coordinates with the syntax as specified in the pydoc:\
	\nfetchs the numbers and returns them in a list.'
	numbers = re.sub("[)(,<)]+"," ",s)[1:-1].split(" ")
	if not (len(n) == 4):
		raise CustomException("malformed tiles tuples")
	return [ int(x) for x in numbers ]

def isValidFile(s, type):
	'checks if the filename is valid. Not only that it still exists but also that it contains the correct xml tree\
	\ns is the path to the file\
	\ntype is the type of the file'
	return os.path.isfile(s) and ET.parse(s).getroot().tag == type

def replace(args):
	'on room, replaces the tiles as follows:\
	\nthe room where the replacement takes place is in the variable room.\
	\nthe tileSet where the tile to be replaced is located is in the variable ts_dst\
	\nthe tileSet where the tile to replace is located is in the variable ts_src\
	\nargs[0] and args[1] are the position of the destination tile within the tileSet (the one to be replaced)\
	\nargs[2] and args[3] are the position of the source tile within the tileSet (the one to replace)\
	\nif there is any ocurrence of destination tile within room, it will be replaced with the source tile'
	global ts_dst, ts_src
	if not (ts_dst.withinLimits(arg[0],arg[1]) and ts_src.withinLimits(arg[2],arg[3])):
		raise CustomException("tile coordinates out of tileSet limits.")
	for tag in room.getroot().iter('tile'):
		if tag.get("bgName")==ts_dst.name and (tag.get("xo"), tag.get("yo")) == ts_dst.posToCoord(args[0],args[1]):
			tag.set("bgName", ts_src.name)
			coord=ts_src.posToCoord(arg[2],arg[3])
			tag.set("xo",coord[0])
			tag.set("yo",coord[1])

def apply(t):
	't is a tuple where t[0] is a function and t[1] is the argument\
	\nthis function applies the funcion t[0] with the argument t[1]'
	return t[0](t[1])

def parse(s):
	global execStack
	processedString = ""
	lastWord = ""
	context = None
	s = re.sub("\s+"," ",s)
	sentence = collapse(s, " ").split(" ")
	try:
		for word in sentence:
			#debug only
			#print word

			processedString += " "+word
			if isQuitWord(word):
				clear()
				print "execution aborted"
				return 1

			if isReserved(word):
				if isReserved(lastWord):
					raise CustomException("unexpected reserved word.")
					break
				context = word.lower()
				continue
			elif context == None:
				raise CustomException("expecting reserved word.")
				break

			if context == "in":
				word = prepareFileName(word,"room")
				if not os.path.isfile(word):
					raise CustomException("expecting room file.")
					break
				execStack.append((loadRoom,word))
				context = None
			elif context == "replace":
				word = prepareFileName(word,"background")
				if not os.path.isfile(word):
					raise CustomException("expecting background file.")
					break
				execStack.append((loadDst,word))
				context = None
			elif context == "with":
				word = prepareFileName(word,"background")
				if not os.path.isfile(word):
					raise CustomException("expecting background file.")
					break
				execStack.append((loadSrc,word))
				context = None
			elif context == "set":
				if isSpecial(word):
					context = word.lower()
				else:
					raise CustomException("Expecting keyword.")
					break
			elif context == "unset":
				if isSpecial(word):
					execStack.append((unset,word))
				else:
					raise CustomException("Expecting keyword.")
					break
			elif context == "roomfolder":
				execStack.append((setRoomFolder,word))
				context = None
			elif context == "backgroundfolder":
				execStack.append((setBackgroundFolder,word))
				context = None
			elif context == "abbreviation":
				try:
					int(word)
				except:
					raise CustomException("Expected either 1 or 0.")
					break
				execStack.append((setAbbreviation,int(word)))
				context = None
			elif context == "print":
				word = word.lower()
				if word == "roomfolder":
					execStack.append((customPrint,roomFolder))
				elif word == "backgroundfolder":
					execStack.append((customPrint,backgroundFolder))
				elif word == "abbreviation":
					execStack.append((customPrint,abbreviation))
				context = None
			elif context == "tiles":
				positions = parseTiles(word)
				execStack.append(replace, positions)

			lastWord=word.lower()
		if not (context == None or context == "tiles"):
			raise CustomException("unexpected end of statement.")
		return 0
	except CustomException as inst:
		print "SYNTAX ERROR: "+str(inst)+"\n"+processedString+" <<<"
		clear()
		return 0

def execute():
	global execStack
	try:
		for action in execStack:
			apply(action)
	except CustomException as inst:
		print "EXECUTION-TIME ERROR: " + str(inst)
		clear()
	cleanExecution()

def save():
	global room_registry
	try:
		for roomName, roomTree in room_registry.iteritems():
			roomTree.write(roomName)
	except:
		print "ERROR DURING SAVING ROUTINE."
		clear()

def main(args):
	if len(args) == 1:
		print "\ninterpreter mode engaged\nto display the manual, type help.\n"
		while True:
			userInput = raw_input("--> ")
			if userInput.lower() == "help":
				help()
			else:
				if parse(userInput) == 1:
					break
				execute()
				save()

	elif args[1] == "-f":
		if len(args) < 3:
			print "file not provided."
		elif not os.path.isfile(args[2]):
			print "'"+args[2]+"' is not a file"
		else:
			file = open(args[2],"r")
			parse(file.read())
			execute()
			save()
			file.close()
		return
	else:
		parse(" ".join(args[1:]))
		execute()
		save()

if __name__=="__main__":
	main(sys.argv)