'''
Created on 5 Jul 2020

Modified 29 Sep 2022

@author: thomasgumbricht

Notes
-----
The module jekyllalbum.py:

    requires that you have ImageMagick setup for your machine, that you have the SoSSImple (v 2) Jekyll theme
    a json file for parameters linking to a txt file listing the photos to import. 
     
    The script takes 2 string parameters as input:
    
        - docpath: the full path to a folder that must contain the txt file as given by the "projFN" parameter
        - projFN: the name of an existing txt files that sequentially lists json parameter files to run
    
    
    The individual parameter files (listed in "projFN") must have approximately 40 parameters 
    in a precise nested json structure with dictionaries and lists.
    You can create a template json parameter file by running "def CreateParamJson" (just uncomment under "def SetupProcesses",
    this creates a template json parameter file called "jekyll_album_4_Jekyll-theme_SoSimple.json" in the 
    path given as the parameter "docpath".
    
    The script first run the stand alone "def SetupProcesses" that reads the txt file "projFN" and 
    then sequentialy run the json parameter files listed. 
    
    Each allbum creation (i.e. each json parameter file) is run as a sequence of commands:
    
    - JekyllYaml: creates the markdown yaml header
    - FigClass: processes the listed images using ImageMagick
        - MagickConvertFull: convert images using ImageMagick
        - MagickConvertPage: reduced resolution images from MagickConvertFull if requested
    - WritePost: Write the makrdown ffor the Jekyll theme soSimple (v2).
            
'''

# Standard library imports

import sys

import os

import subprocess

# Third party imports

import json

from PIL import Image

from PIL.ExifTags import TAGS

def JekyllAlbumJson():
    """ Create a template dictionary for parametising this script
    
    
        :returns: template parameters 
        :rtype: dict
        
    """
    
    paramD =     {
      "overwrite": True,
      "media": {
        "srcfp": "path/to/image/library",
        "listfn": "album.txt",
        "labelsfn": False,
        "magickfn": False
      },
      "urlimages": {
        "xdim": 1200,
        "ydim": 0,
        "kind": "jpg",
        "quality": 80,
        "suffix": "m"
      },
      "inpageimages": {
        "xdim": 300,
        "ydim": 0,
        "kind": "jpg",
        "quality": 70,
        "suffix": "s"
      },
      "imagemagick": {
        "convert": {
          "-auto-gamma": ""
        },
        "dissolve": 50,
        "alpha": 0,
        "emboss": False,
        "watermark": {
          "-font": "Arial",
          "-pointsize": "250",
          "-gravity": "center",
          "-draw": "fill 'RGBA(32,32,64,0.25)' text 2,2 'KARTTUR' fill 'RGBA(255,255,255,0.25)' text -2,-2 'EMBOSS' fill grey text 0,0 'EMBOSS' ",
          "-transparent": "grey",
          "-fuzz": "90%"
        }
      },
      "metadata": {
        "author": "Author Name",
        "datetime": "YYYYMMDD",
        "country": "country",
        "location": "Placename(s)",
        "movemode": "foot",
        "lon": 18.080822,
        "lat": 59.374705,
        "elev": -999,
        "yaw": 0,
        "pitch": 0,
        "roll": 0
      },
      "content": {
        "rolltitle": "title",
        "figcaption": "figure cpation. ",
        "description": "short desicription.",
        "persons": [
          "N N",
          "M M"
        ],
        "keywords": [
          "key1",
          "key2",
          "key3"
        ]
      },
      "publication": {
        "quality": 3,
        "public": 2,
        "paltyp": 2,
        "figclass": "third",
        "layout": "post",
        "categories": "existing category in you SoSimple structure",
        "dstfp": "destination folder of your local SoSimple setup"
      }
    }
    
    return (paramD)

def CreateParamJson(docpath):
    """ Create the default json parameters file structure, only to create template if lacking
    
        :param str docpath: directory path   
    """
    
    # Get the default params
    paramD = JekyllAlbumJson()
    
    # Set the json FPN
    jsonFPN = os.path.join(docpath, 'jekyll_album_4_Jekyll-theme_SoSimple.json')
    
    # Dump the paramD as a json object
    jsonF = open(jsonFPN, "w")
  
    json.dump(paramD, jsonF, indent = 2)
  
    jsonF.close()

def JekyllYaml(pD):
    """ Build the Jekyll album Yaml header
    
        :param pD: album parameters
        :type pD: dict
        
        :returns: yaml header 
        :rtype: list
    """

    yamlDate = '%(y)s-%(m)s-%(d)s' %{'y':pD['metadata']['datetime'][0:4], 
                                     'm':pD['metadata']['datetime'][4:6],
                                     'd':pD['metadata']['datetime'][6:8]}
             
    yamlL = ['---', 'layout: %s' % pD['publication']['layout'], 
             'title: %s' % pD['content']['rolltitle'],
             'categories: %s' % pD['publication']['categories'], 
             'excerpt: %s' % pD['content']['description'],
             'tags:']
             
    for item in pD['content']['keywords']:
    
        yamlL.append(' - %s' % item)
        
    yamlL.extend( ['date: %s' % yamlDate, 
                   'modified: %s' % yamlDate,
                    'comments: true', 
                    'share: true', '---' ] )
        
    return yamlL


        
def GetImageMeta(srcImageFPN, dstJsonMetaFPN):
    """ Retrieve image exifdata (metadata) using PIL, write to json file and return
        
        :param srcImageFPN: path to image source file
        :type srcImageFPN: str
        
        :param dstJsonMetaFPN: path to destination metadata file
        :type dstJsonMetaFPN: str
        
        :returns: meatadata 
        :rtype: dict
    """
    
    metaD = {}
    img = Image.open(srcImageFPN)
    
    exifdata = img.getexif()
    
    for tag_id in exifdata:
                
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        
        data = exifdata.get(tag_id)
        
        # decode bytes 
        if isinstance(data, bytes):
            
            data = data.decode()
                                                 
        metaD[tag] = data
       
    metaxD = {}
    
    for tag in metaD:
        
        if isinstance(metaD[tag], str): 
                      
            metaD[tag] =  metaD[tag].rstrip('\x00')
            
            if len(metaD[tag]) == 0:
                
                continue   
            
        elif isinstance(metaD[tag], int): 
            
            metaD[tag] = int(str(metaD[tag]))
            
        elif isinstance(metaD[tag], float): 
            
            metaD[tag] = float(str(metaD[tag]))
            
        else:
            
            continue
            
        metaxD[tag] = metaD[tag]
            
    jsonF = open(dstJsonMetaFPN, "w")
  
    json.dump(metaxD, jsonF, indent = 2)
  
    jsonF.close()
        
    return metaxD
    
def MagickConvertPage(pD, dstFullFPN, dstPageFPN):
    """ ImageMagick reduction of size and quality of the destination image to a smaller, in-page image
        
        :param pD: process parameters
        :type pD: dict
        
        :param dstFullFPN: path to larger, existing (url-linked) destination image
        :type dstFullFPN: str
    
        :param dstPageFPN: path to smaller (in-page) destination image
        :type dstPageFPN: str
    """
    
    #Here is the conversion
    if int(pD['inpageimages']['xdim']) and int(pD['inpageimages']['ydim']):
    
        resize = '%sx%s' %(pD['inpageimages']['xdim'], pD['inpageimages']['ydim'])
        
    elif int(pD['inpageimages']['xdim']):
    
        resize = '%sx' %(pD['inpageimages']['xdim'])
        
    elif int(pD['inpageimages']['ydim']):
    
        resize = 'x%s' %(pD['inpageimages']['ydim'])
        
    else:
    
        resize = False
        
    quality = str(pD['inpageimages']['quality'])
    
    cmdL = ['/usr/local/bin/convert', '-resize', resize, '-quality', quality, dstFullFPN, dstPageFPN]
    
    subprocess.run(cmdL)

def MagickConvertFull(pD, srcImageFPN, dstFullFPN, tempFPN):
    """ Process image source using ImageMAgick and save to destination path(s)
    
        :param pD: process parameters
        :type pD: dict
        
        :param srcImageFPN: path to the source image
        :type srcImageFPN: str
        
        :param dstFullFPN: path to larger (url-linked) destination image
        :type dstFullFPN: str
    
        :param tempFPN: path to temporary image file
        :type tempFPN: str
    """
    #Here is the conversion
    if int(pD['urlimages']['xdim']) and int(pD['urlimages']['ydim']):
    
        resize = '%sx%s' %(pD['urlimages']['xdim'], pD['urlimages']['ydim'])
        
    elif int(pD['urlimages']['xdim']):
    
        resize = '%sx' %(pD['urlimages']['xdim'])
        
    elif int(pD['urlimages']['ydim']):
    
        resize = 'x%s' %(pD['urlimages']['ydim'])
        
    else:
    
        resize = False
        
    quality = str(pD['urlimages']['quality'])
        
    if pD['imagemagick']:
        
        convertCmd = []
        
        for k,v in pD['imagemagick']['convert'].items():
            convertCmd.append(k)
            if v:
                convertCmd.append( str(v) )
    
        convertCmd = ','.join(convertCmd)

    else:
    
        convertCmd = False
        
    if resize: 
        
        if convertCmd:
            
            cmdL = ['/usr/local/bin/convert', '-resize', resize, convertCmd, '-quality', quality, srcImageFPN, dstFullFPN]
        
        else:
            cmdL = ['/usr/local/bin/convert', '-resize', resize, '-quality', quality, srcImageFPN, dstFullFPN]
    
    else: 
        if convertCmd:
            
            cmdL = ['/usr/local/bin/convert',  convertCmd, '-quality', quality, srcImageFPN, dstFullFPN]
        
        else:
            cmdL = ['/usr/local/bin/convert',  '-quality', quality, srcImageFPN, dstFullFPN]

    subprocess.run(cmdL)
    
    if pD['imagemagick']['dissolve']:
            
        # Resize the original images
        cmdL = ['/usr/local/bin/convert', '-resize', resize, srcImageFPN, tempFPN]
        
        subprocess.run(cmdL)
        
        # composite the old and new image with the dissolve set
        cmdL = ['/usr/local/bin/composite', '-dissolve', str(pD['imagemagick']['dissolve']),  tempFPN, dstFullFPN, dstFullFPN];
    
        subprocess.run(cmdL)
        
    if pD['imagemagick']['alpha']:
        
        pass
        # Not yet implemented
        
    if pD['imagemagick']['emboss']:
        
        img = Image.open(dstFullFPN)
  
        # get width and height
        w = img.width
        
        h = img.height

        cmdL = ['/usr/local/bin/convert', '-size', '%sx%s' %(w,h), 'xc:none',]
        
        for k,v in pD['imagemagick']['watermark'].items():

            cmdL.append( k )
            cmdL.append( v )
            
        cmdL.append( tempFPN )

        subprocess.run(cmdL)
         
        # Composite the embossed text and the fixed image 
        cmdL = ['/usr/local/bin/composite',  tempFPN, dstFullFPN, dstFullFPN];
        
        subprocess.run(cmdL)
        
def FigClass(pD, jsonFPN):
    """ Process figures (images, photos) using ImageMagick
    
        :param pD: parameters for creating jekyll album
        :type pD: dict
        
        :param jsonFPN: path to json parameter file
        :type jsonFPN: str
        
        :return bodyL: markdown body text
        :rtype bodyL: list
    """
    
    srcFP, rollName = os.path.split(jsonFPN)
    
    rollName = os.path.splitext(rollName)[0]
    
    bodyL = []
    
    heading1 = '#### %s' %(pD['content']['description'])
    
    bodyL.append(heading1)
    
    who = '%s %s' %( '**Who:**', ', '.join(pD['content']['persons']) )
    
    bodyL.append(who)
    
    where = '**Where :** %s (%s)' %( pD['metadata']['location'], pD['metadata']['country'])
    
    bodyL.append(where)
    
    bodyL.append('Mouse over the images to highlight, click to see larger pop-up images.')
        
    if pD['publication']['figclass'] in ['1', 'single', 'none', 'None', 'NA', 'na']:
        bodyL.append('<figure>')
        
    elif pD['publication']['figclass'] == 'half':
        bodyL.append("<figure class='half'>")
        
    elif pD['publication']['figclass'] == 'third':
        bodyL.append("<figure class='third'>")
        
    else:
        sys.exit('unknown figclass')
        
    # Create target folder
    tarFP = pD['publication']['dstfp']
            
    photoFP = os.path.join(tarFP,'photos')
        
    rollFP = os.path.join(photoFP,rollName)
    
    if not os.path.exists(rollFP):
        os.makedirs(rollFP)
            
    # Get the list of images
    listFPN = os.path.join(pD['media']['srcfp'], pD['media']['listfn'])
    
    with open(listFPN) as file:
    
        lines = file.readlines()
        
        lines = [line.rstrip() for line in lines]
    
    for file in lines:
            
        srcImageFPN = file
        
        FN = os.path.split(file)[1]
        
        dstFullFN = dstPageFN = '%s_%s_%s.%s' %(rollName, 
                                              pD['urlimages']['suffix'], 
                                              os.path.splitext(FN)[0], 
                                              pD['urlimages']['kind'])
        
        dstjsonMetaFN = '%s_%s_%s.json' %(rollName, 
                                            'meta',
                                              os.path.splitext(FN)[0] )
  
        
        dstFullFPN = dstPageFPN = os.path.join(rollFP,dstFullFN)
        
        dstjsonMetaFPN = os.path.join(rollFP,dstjsonMetaFN)
        
        # Get the image meta data
        metaD = GetImageMeta(srcImageFPN,dstjsonMetaFPN)
        
        tempPFN = os.path.join(rollFP,'temp.png')
        
        if not os.path.isfile(dstFullFPN) or pD['overwrite']:
        
            MagickConvertFull(pD,srcImageFPN, dstFullFPN,tempPFN)
               
        if pD['inpageimages'] != pD['urlimages']:
            
            dstPageFN = '%s_%s_%s.%s' %(rollName, 
                                        pD['inpageimages']['suffix'],
                                        os.path.splitext(FN)[0],
                                        pD['inpageimages']['kind'])
            
            dstPageFPN = os.path.join(rollFP,dstPageFN)
            
            if not os.path.isfile(dstPageFPN) or pD['overwrite']:
            
                MagickConvertPage(pD, dstFullFPN, dstPageFPN)

        bodyL.append('<a href="../../photos/%(fp)s/%(fullfn)s"><img src="../../photos/%(fp)s/%(qlfn)s" alt="image"></a>' %{'fp':rollName, 'fullfn':dstFullFN, 'qlfn':dstPageFN})       

        #bodyL.append('<a href="../../photos/%(fp)s/%(jsonfn)s">%(meta)s</a>' %{'fp':rollName, 'jsonfn':dstjsonMetaFN, 'meta':metaD['DateTime']})       

    bodyL.append("<figcaption>%s</figcaption>" %(pD['content']['figcaption']))
    
    bodyL.append("</figure>")  
      
    return bodyL

def WritePost(pD, jsonFPN, yamlL, bodyL):
    """ Write the album post as a markdown file
    
        :param pD: parameters for creating jekyll album
        :type pD: dict
        
        :param jsonFPN: path to json parameter file
        :type jsonFPN: str
        
        :param yamlL: markdown yaml text lines
        :type pD: list
        
        :param bodyL: markdown body text lines
        :type bodyL: list

    """

    yamlDate = '%(y)s-%(m)s-%(d)s' %{'y':pD['metadata']['datetime'][0:4], 
                                     'm':pD['metadata']['datetime'][4:6],
                                     'd':pD['metadata']['datetime'][6:8]}

    year = pD['metadata']['datetime'][0:4]
    
    rollName = os.path.split(jsonFPN)[1]
    
    rollName = os.path.splitext(rollName)[0]
    
    # Create target folder
    tarFP = pD['publication']['dstfp']
        
    yearFP = os.path.join(tarFP,'_posts',year)
    
    if not os.path.exists(yearFP):
        os.makedirs(yearFP)
        
    postFN =  '%s-%s.md' %(yamlDate, rollName)
    
    postFPN = os.path.join(yearFP, postFN)
    
    if not os.path.isfile(postFPN) or pD['overwrite']:

        f = open(postFPN, 'w')
        
        for row in yamlL:
    
            f.write (row)
            
            f.write ('\n')
            
        f.write ('\n')
        
        for row in bodyL:
        
            f.write ('\n')
                        
            f.write (row)
            
            f.write ('\n')
        
def PilotJekyllAlbum(jsonFPN):
    """ Create Jekyll photo album from json command file

        :param jsonFPN: path to xml file
           :type jsonFPN: str
    """
    
    # Parse the json file
    with open(jsonFPN) as jsonF:
    
        pD = json.load(jsonF)
  
    # Create the Jekyll Yaml    
    yamlL = JekyllYaml(pD)
         
    # Create the markdown      
    bodyL = FigClass(pD, jsonFPN)
    
    WritePost(pD, jsonFPN, yamlL, bodyL)
    
def SetupProcesses(docpath, projFN):   
    '''Setup and loop processes
    
    :paramn docpath: path to text file 
    :type: lstr
            
    :param projFN: project filename
    :rtype: str
            
    '''
    
    ''' CreateParamJson creates the default json structure for running the python script, 
    only use it to create a backbone then edit 
    
    CreateParamJson(docpath)
    '''
    
    srcFP = os.path.join(os.path.dirname(__file__),docpath)

    projFPN = os.path.join(srcFP,projFN)

    # Get the full path to the project text file
    dirPath = os.path.split(projFPN)[0]

    if not os.path.exists(projFPN):

        exitstr = 'EXITING, project file missing: %s' %(projFPN)

        exit( exitstr )

    infostr = 'Processing %s' %(projFPN)

    print (infostr)

    # Open and read the text file linking to all json files defining the project
    with open(projFPN) as f:

        jsonL = f.readlines()

    # Clean the list of json objects from comments and whithespace etc
    jsonL = [os.path.join(dirPath,x.strip())  for x in jsonL if len(x) > 10 and x[0] != '#']

    #Loop over all json files and create Schemas and Tables
    for jsonObj in jsonL:
        
        print ('jsonObj:', jsonObj)
                                
        PilotJekyllAlbum(jsonObj)
        
if __name__ == '__main__':
    """
    """
    
    docpath = "/Volumes/karttur/bilder/se"
    
    projFN = ("jekyllalbums_se.txt")
    
    SetupProcesses(docpath, projFN)
    