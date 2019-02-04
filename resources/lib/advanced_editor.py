import json
import utils as utils
import xbmcvfs
import xbmc
import xbmcgui

class BackupSetManager:
    jsonFile = xbmc.translatePath(utils.data_dir() + "custom_paths.json")
    paths = None
    
    def __init__(self):
        self.paths = {}
        
        #try and read in the custom file
        self._readFile()

    def addSet(self,aSet):
        self.paths[aSet['name']] = {'root':aSet['root'],'dirs':[{"type":"include","path":aSet['root'],'recurse':True}]}

        #save the file
        self._writeFile()

    def updateSet(self,name,aSet):
        self.paths[name] = aSet

        #save the file
        self._writeFile()

    def deleteSet(self,index):
        #match the index to a key
        keys = self.getSets()

        #delete this set
        del self.paths[keys[index]]

        #save the file
        self._writeFile()
    
    def getSets(self):
        #list all current sets by name
        keys = self.paths.keys()
        keys.sort()

        return keys

    def getSet(self,index):
        keys = self.getSets();

        #return the set at this index
        return {'name':keys[index],'set':self.paths[keys[index]]}

    def _writeFile(self):
        #create the custom file
        aFile = xbmcvfs.File(self.jsonFile,'w')
        aFile.write(json.dumps(self.paths))
        aFile.close()
    
    def _readFile(self):
        
        if(xbmcvfs.exists(self.jsonFile)):

            #read in the custom file
            aFile = xbmcvfs.File(self.jsonFile)

            #load custom dirs
            self.paths = json.loads(aFile.read())
            aFile.close()
        else:
            #write a blank file
            self._writeFile()

class AdvancedBackupEditor:
    dialog = None

    def __init__(self):
        self.dialog = xbmcgui.Dialog()

    def createSet(self):
        backupSet = None
    
        name = self.dialog.input(utils.getString(30110),defaultt='Backup Set')

        if(name != None):

            #give a choice to start in home or enter a root path
            enterHome = self.dialog.yesno(utils.getString(30111),line1=utils.getString(30112) + " - " + utils.getString(30114),line2=utils.getString(30113) + " - " + utils.getString(30115),nolabel=utils.getString(30112),yeslabel=utils.getString(30113))

            rootFolder = 'special://home'
            if(enterHome):
                rootFolder = self.dialog.input(utils.getString(30116),defaultt=rootFolder)

                #direcotry has to end in slash
                if(rootFolder[:-1] != '/'):
                    rootFolder = rootFolder + '/'

                #check that this path even exists
                if(not xbmcvfs.exists(xbmc.translatePath(rootFolder))):
                    self.dialog.ok(utils.getString(30117),utils.getString(30118),rootFolder)
                    return None
            else:
                #select path to start set
                rootFolder = self.dialog.browse(type=0,heading=utils.getString(30119),shares='files',defaultt=rootFolder)

            backupSet = {'name':name,'root':rootFolder}
    
        return backupSet

    def editSet(self,name,backupSet):
        optionSelected = ''
    
        while(optionSelected != -1):
            options = [utils.getString(30120),utils.getString(30121) + ": " + backupSet['root']]

            for aDir in backupSet['dirs']:
                if(aDir['type'] == 'exclude'):
                    options.append(utils.getString(30129) + ': ' + aDir['path'])

            optionSelected = self.dialog.select(utils.getString(30122) + ' ' +  name,options)

            if(optionSelected == 0):
                #add an exclusion
                excludeFolder = self.dialog.browse(type=0,heading=utils.getString(30120),shares='files',defaultt=backupSet['root'])

                #will equal root if cancel is hit
                if(excludeFolder != backupSet['root']):
                    backupSet['dirs'].append({"path":excludeFolder,"type":"exclude"})
            elif(optionSelected == 1):
                self.dialog.ok(utils.getString(30121),utils.getString(30130),backupSet['root'])
            elif(optionSelected > 1):
                #remove exclusion folder
                del backupSet['dirs'][optionSelected - 2]

        return backupSet
    

    def showMainScreen(self):
        exitCondition = ""
        customPaths = BackupSetManager()

        #show this every time
        self.dialog.ok(utils.getString(30036),utils.getString(30037))
 
        while(exitCondition != -1):
            #load the custom paths
            options = [xbmcgui.ListItem(utils.getString(30126),'',utils.addon_dir() + '/resources/images/plus-icon.png')]
        
            for index in range(0,len(customPaths.getSets())):
                aSet = customPaths.getSet(index)
                options.append(xbmcgui.ListItem(aSet['name'],utils.getString(30121) + ': ' + aSet['set']['root'],utils.addon_dir() + '/resources/images/folder-icon.png'))
            
            #show the gui
            exitCondition = self.dialog.select(utils.getString(30125),options,useDetails=True)
        
            if(exitCondition >= 0):
                if(exitCondition == 0):
                    newSet = self.createSet()

                    customPaths.addSet(newSet)
                else:
                    #bring up a context menu
                    menuOption = self.dialog.select(heading=utils.getString(30124),list=[utils.getString(30122),utils.getString(30123)],preselect=0)

                    if(menuOption == 0):
                        #get the set
                        aSet = customPaths.getSet(exitCondition -1)

                        #edit the set
                        updatedSet = self.editSet(aSet['name'],aSet['set'])

                        #save it
                        customPaths.updateSet(aSet['name'],updatedSet)
                    
                    elif(menuOption == 1):
                        if(self.dialog.yesno(heading=utils.getString(30127),line1=utils.getString(30128))):
                            #delete this path - subtract one because of "add" item
                            customPaths.deleteSet(exitCondition -1)

    def copySimpleConfig(self):
        #disclaimer in case the user hit this on accident
        shouldContinue = self.dialog.yesno('Copy Config','This will copy the default Simple file selection to the Advanced Editor','This will erase any current Advanced Editor settings')

        if(shouldContinue):
            source = xbmc.translatePath(utils.addon_dir() + "/resources/data/default_files.json")
            dest = xbmc.translatePath(utils.data_dir() + "/custom_paths.json")

            xbmcvfs.copy(source,dest)

              
