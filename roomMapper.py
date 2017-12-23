"""
README!
this python script has been made by @gommness (AKA @PinkOnion_)

This script may be used with a Game Maker Studio project. I am not sure if it works for Game Maker Studio 2 but it may work.
The purpose of this script is to read data from a room file and create a jpeg file that is a scaled picture of said room
be aware that this script uses instance information to draw the maps.
"""



"""
the following vars can be modified so the parameters adjust those of your game. Please read the comments trying to explain what
each thing does. Plus, if you have any doubts, feel free to ask me via twitter @PinkOnion_   <3
"""

#these vars represent the scale of your representation. For example, you may have a gridSize of 32 and you may want to
#represent 32 pixels of your room as 8 pixels of your jpeg. That is, represent the room scale 8:32
#be aware that the output gets a bit dirty if your output resolution is way too small (for example, if factor is less than 8)
#also, if gridSize is not divisible by factor, then the results may not be very accurate
gridSize = 32
factor = 8

#this list of lists has the separated sets of instances that will be drawn.
#we separate the instances in sets because each set will be drawn separatedly. Thus, we can specify which instances we want
#to draw after (that is, on top) of the others. The later Lists of instances will be drawn last
#please keep in mind that the names on these lists are none other than the names that you've chosen for your objects in GM:S
#as an example, in my images I wanted to draw water before anything else (so that solids appear over it), thus I included it in a list apart from the rest
instances = [
	["obj_water", ],
	["obj_thin_wall", "obj_wall", "obj_breakable_block", "obj_key", "obj_lock"],
	]

#this is a dictionary that associates instances with colors
#The keys of the dictionary must be your instance names. The value of each key must be a color (A string that represents a color in this case)
#you can add new entries to it.
#please look at the Pillow documentation for color names
col = {
	"obj_wall" : "yellow",
	"obj_breakable_block" : "orange",
	"obj_key" : "green",
	"obj_lock" : "black",
	"obj_thin_wall" : "red",
	"obj_water" : "blue",
	"default" : "gray",
}










##############################################################################
#                                                                            #
#  don't change anything below this point unless you know what you're doing  #
#                                                                            #
##############################################################################

print "\nthanks for using this script!"
print "author's twitter: @gommness or @PinkOnion_   come by and say hi!"
try:
	from PIL import Image, ImageDraw
except:
	print "you need Pillow to run this script!.\nplease download Pillow by using: pip install Pillow\n"
	sys.exit(1)
import xml.etree.ElementTree as ET
import sys
import os

invfactor = gridSize/factor
inputf = ""
outputf = ""

if len(sys.argv) == 2:#this means that te output jpeg is named after the room filename
	aux = sys.argv[1]
	inputf = os.path.join("rooms", aux)
	os.path.isdir("maps")
	outputf = aux.split(".")[0]
elif len(sys.argv) == 3:#this means that the output jpeg has been passed via argv
	inputf = os.path.join("rooms",sys.argv[1])
	outputf = sys.argv[1]
else:
	print "unvalid arguments. Command: \"python roomMapper.py <<inputFile>> [<<outputFile>>]\""
	sys.exit(1)

#now we check whether the "maps" directory exists, since our output.jpeg will be saved there
if os.path.isdir("maps"):
	outputf = os.path.join("maps",outputf)
else:
	print "there is no \"maps\" directory. The .jpeg will be created at current directory"

#we now strip away any unwanted extensions and fix them to work with .room.gmx for the input and .jpeg for the output
inputf = inputf.split(".")[0]+".room"+".gmx"
outputf = outputf.split(".")[0]+".jpeg"


#now we try to open the input file and read as a xml tree
try:
	xmlRoom = ET.parse(inputf)
except:
	print "unable to open the file \""+inputf+"\""
	sys.exit(1)
#we get the root of the document and the width and height of the room, scaled to our new dimensions
root = xmlRoom.getroot()
width = int(root.find("width").text)/factor
height = int(root.find("height").text)/factor

#then we initialize the Pillow objects that will do the drawing
imageOut = Image.new("RGB", (width,height), "grey")
draw = ImageDraw.Draw(imageOut)


for instanceSet in instances:
	for w in root.iter("instance"):
		objName = w.get("objName")
		if objName in instanceSet:
			x = int( float(w.get("x"))/factor)
			y = int( float(w.get("y"))/factor)
			scaleX = int( float(w.get("scaleX")))
			scaleY = int(float(w.get("scaleY")))
			#debug only print statement
			#print "OBJ: "+objName+" X: "+str(x)+" Y: "+str(y)+" XX: "+str(scaleX)+" YY: "+str(scaleY)
			draw.rectangle(((x,y),(x+scaleX*invfactor - 1,y+scaleY*invfactor - 1)), fill=col[objName])


imageOut.save(outputf,"JPEG")
print "the image "+outputf+" has been created succesfully!"
