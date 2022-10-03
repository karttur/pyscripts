'''
Created on 10 Sep. 2019

updated 11 Jun 2020

updated 3 Oct 2020

@author: thomasgumbricht
'''

# Standard imports

import os, sys

import json

import hashlib

def RemoveMatchingPathsParams():
    ''' Default parameters for removing duplicates in matching paths
    
        :returns: parameter dictionary
        :rtype: dict
    '''
    
    paramD = {}
    
    paramD['verbose'] = 1
    
    paramD['mainFP'] = 'path/to(main/folder/to/keep'
    
    paramD['examFPL'] = ['list','paths','to','examine']
    
    paramD['remove'] = {}
    
    paramD['remove']['removeDuplicate'] = True
    
    paramD['remove']['removeDSstore'] = True
    
    paramD['remove']['removeHidden'] = True
    
    paramD['remove']['removeRoot'] = False
    
    paramD['remove']['removeAllDupl'] = False
    
    paramD['remove']['removeSmallerOlder'] = False
    
    paramD['deleleExtL'] = ['list','of','extensions','to','delete']
     
    return (paramD)

def CreateParamJson(docpath):
    """ Create the default json parameters file structure, only to create template if lacking
    
        :param str docpath: directory path   
    """
    
    # Get the default params
    paramD = RemoveMatchingPathsParams()
    
    # Set the json FPN
    jsonFPN = os.path.join(docpath, 'remove_matching_paths.json')
    
    # Dump the paramD as a json object
    jsonF = open(jsonFPN, "w")
  
    json.dump(paramD, jsonF, indent = 2)
  
    jsonF.close()

def ReadRemoveMatchingPathsJson(jsonFPN):
    """ Read the parameters for remving matching paths
    
    :param jsonFPN: path to json file
    :type jsonFPN: str
    
    :return paramD: parameters
    :rtype: dict
   """
    
    with open(jsonFPN) as jsonF:
    
        paramD = json.load(jsonF)
        
    return (paramD)

def Hashfile(path, blocksize = 65536):
    """  Calculate hash for file
    
        :param str path: file path
        
        :param int blocksize: blocksize to use when reading file
        
        :returns: hex-encoded string
        :rtype: str
    """
    
    afile = open(path, 'rb')
    
    hasher = hashlib.md5()
    
    buf = afile.read(blocksize)
    
    while len(buf) > 0:
        
        hasher.update(buf)
        
        buf = afile.read(blocksize)
        
    afile.close()
    
    return hasher.hexdigest()   

def RemoveMatchingPaths(mainpath, exampath, removeHidden=True, removeDSstore = True, removeAllDupl=False, removeSmallerOlder=False, deleleExtL=[]):
    """ Search ad delete matching files and subfolders
        
        :param str mainpath: root folder path for main directory to keep
        
        :param str exampath: root folder path for examination directory to clean
        
        :param bool removeHidden: Remove duplicates of hidden files 
        
        :param bool removeDSstore: Remove duplicates of .DSstore (macOS) 
        
        :param bool removeAllDupl: remove file if full path is identical, disregarding md5 hash
        
        :param bool removeSmallerOlder: remove file if full path is identical and examined copy is smaller and older
    
        :param list deleleExtL: List of file extensions to delete; if list == ['*'] all identified copies are deleted
    """
    
    if mainpath == exampath:
        
        sys.exit('EXITING mainpath == exampath')
        
    if not os.path.isdir(mainpath):
        
        sys.exit('EXITING mainpath does not exist',mainpath)
        
    if not os.path.isdir(exampath):
        
        sys.exit('EXITING exampath does not exist',exampath)
        
    for root, dirs, nofiles in os.walk(mainpath, topdown=True):
        
        if not removeHidden:
            
            dirs[:] = [d for d in dirs if not d[0] == '.']
            
        for subdir in dirs:
            
            mainsubpath = os.path.join(root,subdir)
            
            examsubroot = root.replace(mainpath, exampath)
            
            examsubpath = os.path.join(examsubroot,subdir)
            
            if os.path.isdir(examsubpath):
                
                #if removeDSstore, just remove it directly
                if removeDSstore:
                    
                    dsStore = os.path.join(examsubpath,'.DS_Store')
                    
                    if os.path.isfile(dsStore):
                        
                        os.remove(dsStore)
                        
                # list and loop files in the main path under examination      
                for file in os.listdir(mainsubpath):
                    
                    if file[0] == '.' and not removeHidden:
                        
                        continue
                    
                    mainFile = os.path.join(mainsubpath,file)
                    
                    if os.path.isfile(mainFile):

                        # Gett he corresponding file name in the exam path
                        examFile = os.path.join(examsubpath,file)
                        
                        # if the exampath has a copy of the main path file
                        if os.path.isfile(examFile):
                            
                            print ('Duplicate file',examsubpath,file)
        
                            if removeAllDupl or deleleExtL[0] == '*':
                                
                                print ('Deleting by name',examFile)
                                
                                os.remove(examFile)
                                
                            elif os.path.splitext(examFile)[1] in deleleExtL:
                                
                                print ('Deleting by extension',examFile)
                                
                                os.remove(examFile)
                                
                            else:  
                                  
                                main_hash = Hashfile(mainFile)
                                
                                exam_hash = Hashfile(examFile)
                                
                                if main_hash == exam_hash:
                                    
                                    print ('Deleting by md5 hash',examFile)
                                                                            
                                    os.remove(examFile)
                                
                                else: # md5 hash not the same
                                      
                                    #Get date and size
                                    examDate = os.path.getmtime(examFile)
                                    
                                    mainDate = os.path.getmtime(mainFile)
                                    
                                    if removeSmallerOlder:
                                        
                                        if examDate < mainDate:
                                            
                                            examSize = os.path.getsize(examFile)
                                            
                                            mainSize = os.path.getsize(mainFile)
                                            
                                            if examSize < mainSize:
                                                
                                                print ('Deleting older and smaller', examFile)

                                                os.remove(examFile)
                                                
                                            else:
                                                print('Content differs, both kept:')
                                                
                                                print ('    ',mainFile)
                                                
                                                print ('    ',examFile)
                                                
                                        else:
                                            print('Content differs, both kept:')
                                            
                                            print ('    ',mainFile)
                                            
                                            print ('    ',examFile)
                                    else:    
                                           
                                        print('Content differs, both kept:')
                                        
                                        print ('    ',mainFile)
                                        
                                        print ('    ',examFile)
                                        
                                print ('')

def RemoveEmptyFolders(path):
    """ Remove empty directories
    
        :param str path: folder path to check if empty and remove
    """

    if not os.path.isdir(path):
        
        return

    files = os.listdir(path)
    
    if len(files):
        
        for f in files:
            
            fullpath = os.path.join(path, f)
            
            if os.path.isdir(fullpath):
                
                RemoveEmptyFolders(fullpath)
    
    # if folder empty, delete it
    files = os.listdir(path)
    
    if len(files) == 0:
        
        print ("Removing empty folder:", path)
        
        os.rmdir(path)
        
    elif len(files) == 1 and files[0] == '.DS_Store':
        
        os.remove(os.path.join(path,'.DS_Store'))
        
        os.rmdir(path)
                    
def LoopMatchingPaths(mainFP, examFPL, removeHidden, removeDSstore, removeAllDupl, removeRoot, removeSmallerOlder, deleleExtL):
    """
        :param str mainFP: root folder path for main directory to keep
        
        :param list examFPL: root folder paths for examination directory to clean
        
        :param bool removeHidden: Remove duplicates of hidden files 
        
        :param bool removeDSstore: Remove duplicates of .DSstore (macOS) 
        
        :param bool removeAllDupl: remove file if full path is identical, disregarding md5 hash
        
        :param bool removeSmallerOlder: remove file if full path is identical and examined copy is smaller and older
    
        :param list deleleExtL: List of file extensions to delete; if list == ['*'] all identified copies are deleted
    """

    
    loopL = [mainFP]
    
    loopL.extend(examFPL)

    for index, mainFolder in enumerate(loopL):
             
        if not os.path.isdir(mainFolder):
            
            continue

        if index == len(loopL)-1:
            
            break
        
        print ('mainfolder', index, mainFolder)
        
        for examIndex in range(index+1,len(loopL)):
            
            examFolder = loopL[examIndex]

            print ('    examFolder',examFolder)
            
            if not os.path.isdir(examFolder):
                continue
                                 
            examRoot = examFolder
        
            RemoveMatchingPaths(mainFolder, examFolder, removeHidden, removeDSstore, removeAllDupl, removeSmallerOlder, deleleExtL )
                
            RemoveEmptyFolders(examRoot)
            
            
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
        
        paramD = ReadRemoveMatchingPathsJson(jsonObj)

        LoopMatchingPaths(paramD['mainFP'], 
                          paramD['examFPL'], 
                          paramD['remove']['removeHidden'], 
                          paramD['remove']['removeDSstore'], 
                          paramD['remove']['removeAllDupl'], 
                          paramD['remove']['removeRoot'], 
                          paramD['remove']['removeSmallerOlder'], 
                          paramD['deleleExtL'])
                             
if __name__ == "__main__":
    """ If script is run as stand alone
    """
    
    docpath = '/Users/thomasgumbricht/GitHub'
    
    projFN = 'remove_matching_paths.txt'
    
    SetupProcesses(docpath, projFN)
        