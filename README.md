# DoWScarAPIUtility
A very simple python 3.7.4 script that generates scardoc.dat API for original Dawn of War games used by Corsix's Mod Studio to provide autocompletion and function descriptions.

Requires function_list.xml to be present in the same working directory which is distributed with the dawn of war - dark crusade mod tools. You can find it in the <game root>/ModTools/ScarDoc/xml folder if your install is default. All your entries must be inside a <GROUP> tag and have same format as the official ones (the only reason for this is that's how the original file is structured, scardoc.dat used by corsix does not preserve group information. By default this file is missing any costants, you have to add them in manually (can just copy all of the default ones from the example function_list.xml provided here, make sure they're put inside any GROUP tag). Constants use a slightly different format, consult example function_list.xml to see it, it's very simple. Functions print, import are not included by default as well.

The script takes no console arguments, if you wish to change filenames you'll have to edit the python script file.
str_inputXML - xml files based on which it will generate the API
str_outputFilename - name of the file that will be created for the generated API
both variables found near the top of the source code.

To use, simply run the python script with a compatible interpreter version from the same working directory as the directory with the .xml file. It will create and overwrite file scardoc.dat by default without asking so make sure there's no files named the same anywhere in the vicinity. Then file is placed in Corsix's Mod Studio Install Dir/Mod_studio_files. Remember to backup the original.
