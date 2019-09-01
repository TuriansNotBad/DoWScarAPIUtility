# written with Python 3.7.4

import xml.etree.ElementTree as ET
import struct

# Corsix has these as extra
# <FUNCTION name="import">
# 	<RESULT type="VOID"/>
# 	<ARGS>
# 		<ARG type="String" name = "fileName"/>
# 	</ARGS>
# 	<SHORTDESC>Loads data:scar/fileName and executes it.</SHORTDESC>
# </FUNCTION>
# <FUNCTION name="print">
# 	<RESULT type="VOID"/>
# 	<ARGS>
# 		<ARG type="Any" name="s1"/>
# 		<ARG type="Any" name="s2"/>
# 		<ARG type="Any" name="s3"/>
# 		<ARG type="Any" name="..."/>
# 	</ARGS>
# 	<SHORTDESC>Loads data:scar/fileName and executes it.</SHORTDESC>
# </FUNCTION>

str_inputXML = "function_list.xml"
str_outputFilename = "scardoc.dat"

# stores information about a function and writes them to APIs
class DocFunction:

	def __init__( self, name = "", result = "", args = [], fshortdesc = "", fextdesc = "" ):
		self.name = name
		self.result = result
		self.args = args
		self.shortdesc = fshortdesc
		self.extdesc = fextdesc
	
	def toCorsixScarDoc( self, f ):
		# maximum length of a single description line
		# if desc exceeds it will add in a new line symbol at the next space
		max_line_len = 70

		fulldesc = self.shortdesc + "\n\n" + self.extdesc
		# split words into a list to make sure new lines are never inserted mid word
		fulldescwords = fulldesc.split(" ")
		# make the final description string have a maximum of 70 characters per line
		line_len = 0
		fulldesc = ""
		for word in fulldescwords:
			# start concatenating words and include space after each one
			fulldesc += word + " "
			line_len += len(word)
			if ( line_len >= max_line_len ):
				# line length exceeded maximum values, insert new line and reset length counter
				fulldesc += "\n "
				line_len = 0
		
		# write return type
		f.write( struct.pack( "i", len(self.result) ) )
		f.write( self.result.encode("ASCII") )
		# write name
		f.write( struct.pack( "i", len(self.name) ) )
		f.write( self.name.encode("ASCII") )
		# write argument count
		f.write( struct.pack( "i", len(self.args) ) )
		# write arguments
		for arg in self.args:
			# how many bytes we'll need to write in the end
			totalbytes = len(arg[0])
			# if arg[0] is Void argument has no name and space is empty string
			# space used to separate argument type from its name
			space = ""
			if ( len(arg[1]) > 0 ):
				totalbytes += len(arg[1]) + 1
				space = " "
			# length of the argument string
			f.write( struct.pack( "i", totalbytes ) )
			# write argument type and name
			f.write( (arg[0] + space + arg[1]).encode("ASCII") )
		# write description
		f.write( struct.pack( "i", len(fulldesc) ) )
		f.write( fulldesc.encode("ASCII") )
	
	def print( self ):
		print( "Function name: " + self.name )
		print( "  Returns: " + self.result )
		print( "  Arguments: " + str(self.args) )
		print( "  Description: " + self.shortdesc + "\n\n" + self.extdesc )

# stores information about a constant and writes them to APIs
class DocConstant:

	def __init__( self, name = "", value = "", shortdesc = "" ):
		self.name = name
		self.value = value
		self.shortdesc = shortdesc
	
	def toCorsixScarDoc( self, f ):
		# write name
		f.write( struct.pack( "i", len(self.name) ) )
		f.write( self.name.encode("ASCII") )
		# 0 byte indicating a lack of arguments/description/results - a constant
		f.write( struct.pack( "i", 0 ) )

	def print( self ):
		print( "Constant name: " + self.name )
		print( "  Value: " + self.value )
		print( "  Description: " + self.shortdesc )

class DocContainer:

	def __init__( self ):
		self.items = []
	
	def AddFunction( self, name, result, args, fshortdesc, fextdesc ):
		self.items.append( DocFunction( name, result, args, fshortdesc, fextdesc ) )
	
	def AddConstant( self, name, value, shortdesc ):
		self.items.append( DocConstant( name, value, shortdesc ) )
	
	def toCorsixScarDoc( self, filename : str ):
		
		# add additional elements included in corsix's API
		self.AddFunction( "print", "Void", [("Any", "s1"),("Any", "s2"),("Any", "s3"),("Any", "...")], "Loads data:scar/fileName and executes it.", "" )
		self.AddFunction( "import", "Void", [("String", "fileName")], "Loads data:scar/fileName and executes it.", "" )

		# do nothing if we're empty
		if ( len(self.items) <= 0 ): return
		# sort our list alphabetically by name
		self.items.sort( key=lambda i: i.name )

		with open( filename, "wb" ) as f:
			# write how many items is in the scardoc
			f.write( struct.pack( "i", len(self.items) ) )
			# write item to file
			for docItem in self.items: docItem.toCorsixScarDoc( f )
	
	def print( self ):
		for i in self.items: i.print()
		print( len(self.items) )

# returns empty string if argument is not a string
def string_or_default( s ):
	if (not isinstance(s, str)): return ""
	return s

# concatenates descriptions, useful when there are BR or TAB tags in them
def desc_concatenator( desc ):
	result = ""

	if (desc is None): return result
	# if desc isn't empty
	if (isinstance(desc.text, str)):
		# append description to our string so far
		result += desc.text
		# search for any BR\TAB tags in the text and append their tailing text
		for el in desc:
			if (el.tag == "BR"):
				result += "\n" + string_or_default(el.tail)
			elif (el.tag == "TAB"):
				result += "    " + string_or_default(el.tail)
	return result

# program execution starts here
def main():
	# root of xml file
	et_input = ET.parse( str_inputXML ).getroot()
	# initialize storage for our data
	docElements = DocContainer()

	# iterate over all the groups
	for group in et_input:
		# iterate over all the functions
		for function in group:
			
			# set all default values
			fname = function.attrib["name"]
			fresult = "Void"
			fargs = None
			fshortdesc = ""
			fextdesc = ""
			# function result tag
			searcher = function.find( "RESULT" )
			if (searcher is not None): fresult = searcher.attrib["type"]
			# function arguments
			searcher = function.find( "ARGS" )
			if (searcher is not None): fargs = [ (a.attrib["type"], a.attrib["name"]) for a in function[2] ]
			# function short description
			fshortdesc = desc_concatenator( function.find( "SHORTDESC" ) )
			# function additional description
			fextdesc = desc_concatenator( function.find( "EXTDESC" ) )
			
			if (function.tag == "FUNCTION"):
				docElements.AddFunction( fname, fresult, fargs, fshortdesc, fextdesc )
			elif (function.tag == "CONST"):
				fvalue = function.attrib["value"]
				docElements.AddConstant( fname, fvalue, fshortdesc )
	# generate corsix's API
	docElements.toCorsixScarDoc( str_outputFilename )

main()