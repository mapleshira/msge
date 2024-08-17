"""
    Program:    Mapleshira Static Gallery Editor
    Author:     mapleshira
    Website:    neocities.mapleshira.org
    Date:       08/16/24
"""

import json
import os
import wx
from PIL import Image

""" Data structure for gallery definition.
"""
class GalleryJSON:
    def __init__(self):
        self.parsedJSON = None
        self.pictureAmount = None
        self.editHistory = None
        self.editHistoryCurrentIndex = None
        self.filepathLocation = None
        self.allowedFormats = None
        self.dirname = None
        return
    
    def generateJSON(self, filepath):
        self.filepathLocation = filepath + "\\" # This saves the filepath sent in, used in thumbnail creation.
        files = os.listdir(filepath)
        
        tempDir = self.filepathLocation[:-1] # Remove last "\\".
        tempDir = tempDir.split("\\")[-1]
        self.dirname = tempDir # This is used mostly on the Javascript side.
        
        self.parsedJSON = {'metadata': {'title': "Gallery Title", 'desc': "Pre-generated gallery description.", 'prefix': "./" + self.dirname}, # Prefix is to be edited in relation to index.html.
                           'pictureData': {}}
        
        count = 0
        for index in range(len(files)):
            if self.formatParsing(files[index]) == True:
                self.parsedJSON['pictureData'][str(count)] = {}
                self.parsedJSON['pictureData'][str(count)]['picURL'] = files[index]
                self.parsedJSON['pictureData'][str(count)]['title'] = "Entry " + str(count) + " (" + str((files[index])) + ")"
                self.parsedJSON['pictureData'][str(count)]['desc'] = "Description for entry " + str(count) + "."
                self.parsedJSON['pictureData'][str(count)]['date'] = "??/??/??"
                count += 1
        
        self.pictureAmount = len(self.parsedJSON['pictureData'])
        self.editHistory = {}
        self.editHistoryCurrentIndex = 0
        return
    
    def saveJSON(self):
        jsonTitle = self.dirname + ".json"
        #jsonStr = json.dumps(self.parsedJSON)
        with open(self.filepathLocation + jsonTitle, 'w') as saveFile:
            json.dump(self.parsedJSON, saveFile, indent = 4)
        return
    
    def openJSON(self, filepath):
        self.filepathLocation = filepath + "\\" # This saves the filepath sent in, used in thumbnail creation.
        with open(filepath) as tempFile:
            fileContents = tempFile.read()
        self.parsedJSON = json.loads(fileContents)
        if type(self.parsedJSON) == str:
            self.parsedJSON = json.loads(self.parsedJSON)
        self.pictureAmount = len(self.parsedJSON['pictureData'])
        self.editHistory = {}
        self.editHistoryCurrentIndex = 0
        
        tempDir = self.filepathLocation[:-1] # Remove last "\\".
        tempDir = tempDir.split("\\")[-1]
        self.dirname = tempDir # This is used mostly on the Javascript side.
        self.dirname = self.dirname.replace('.json', '')
        
        self.filepathLocation = self.filepathLocation.replace(self.dirname + ".json", '')
        self.filepathLocation = self.filepathLocation[:-1]
    
    def closeJSON(self):
        self.filepathLocation = None
        self.parsedJSON = None
        self.pictureAmount = 0
        self.editHistory = {}
        self.editHistoryCurrentIndex = 0
        
    def addHistoryEntry(self, editIndex, actionType, editString):
        if (self.editHistoryCurrentIndex < len(self.editHistory)):
            self.clearHistory(len(self.editHistory) - self.editHistoryCurrentIndex)
        
        self.editHistoryCurrentIndex += 1 # increase our current history index.
        dictionaryAddition = {
            'dictHist' + str(self.editHistoryCurrentIndex): {
                'editIndex': editIndex,
                'actionType': actionType,
                'editString': editString,
            }
        }
        self.editHistory.update(dictionaryAddition)
        return

    def historyUndo(self):
        if (self.editHistoryCurrentIndex > 0): # if greater than 0 history index.
            undoIndex = self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editIndex']
            undoAction = self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['actionType']
            undoString = self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editString']
            
            if (undoAction == 0): # title
                # setup this edit history index for a possible redo ...
                self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editString'] = self.parsedJSON['pictureData'][undoIndex]['title']
                self.parsedJSON['pictureData'][undoIndex]['title'] = undoString
            elif (undoAction == 1): # desc
                # once again, desc this time.
                self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editString'] = self.parsedJSON['pictureData'][undoIndex]['desc']
                self.parsedJSON['pictureData'][undoIndex]['desc'] = undoString
            elif (undoAction == 1): # date
                # once again, desc this time.
                self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editString'] = self.parsedJSON['pictureData'][undoIndex]['desc']
                self.parsedJSON['pictureData'][undoIndex]['desc'] = undoString
            
            
            self.editHistoryCurrentIndex -= 1 # move backwards through our current history index as we undo.
        return
    
    def historyRedo(self):
        if (self.editHistoryCurrentIndex < len(self.editHistory)): # if there is history to redo then ...
            self.editHistoryCurrentIndex += 1 # move forwards through our redo history.
            redoIndex = self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editIndex']
            redoAction = self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['actionType']
            redoString = self.editHistory['dictHist' + str(self.editHistoryCurrentIndex)]['editString']
            if (redoAction == 0): # title
                self.parsedJSON['pictureData'][redoIndex]['title'] = redoString
            elif (redoAction == 1): # desc
                self.parsedJSON['pictureData'][redoIndex]['desc'] = redoString
            elif (redoAction == 1): # date
                self.parsedJSON['pictureData'][redoIndex]['date'] = redoString
        return
    
    def clearHistory(self, fullClear):
        if (fullClear == True):
            self.editHistoryCurrentIndex = 0
        for x in range(len(self.editHistory) - self.editHistoryCurrentIndex):
            del self.editHistory['dictHist' + str(self.editHistoryCurrentIndex + x + 1)] # add one to match up index with sizes...
        return
    
    def debugGetHistory(self):
        return self.editHistory
    
    def getMetadataTitle(self):
        return self.parsedJSON['metadata']['title'] 
    
    def setMetadataTitle(self, editString):
        # No history for metadata- more confusing since it isn't always on screen.
        self.parsedJSON['metadata']['title'] = editString
        return
    
    def getMetadataPrefix(self):
        return self.parsedJSON['metadata']['prefix'] 
    
    def setMetadataPrefix(self, editString):
        # No history for metadata- more confusing since it isn't always on screen.
        self.parsedJSON['metadata']['prefix'] = editString
        return
    
    def getMetadataDesc(self):
        return self.parsedJSON['metadata']['desc']
    
    def setMetadataDesc(self, editString):
        # No history for metadata- more confusing since it isn't always on screen.
        self.parsedJSON['metadata']['desc'] = editString
        return
    
#    def getMetadataTags(self):
#        return self.parsedJSON['metadata']['desc']
    
    def getPicURL(self, index):
        return self.parsedJSON['pictureData'][index]['picURL']
    
    def getTitle(self, index):
        return self.parsedJSON['pictureData'][index]['title'] 
    
    def setTitle(self, index, editString):
        self.addHistoryEntry(index, 0, self.parsedJSON['pictureData'][index]['title'])
        self.parsedJSON['pictureData'][index]['title'] = editString
        return
    
    def getDesc(self, index):
        return self.parsedJSON['pictureData'][index]['desc']
    
    def setDesc(self, index, editString):
        self.addHistoryEntry(index, 1, self.parsedJSON['pictureData'][index]['desc'])
        self.parsedJSON['pictureData'][index]['desc'] = editString
        return
    
    def getDate(self, index):
        return self.parsedJSON['pictureData'][index]['date']
    
    def setDate(self, index, editString):
        self.addHistoryEntry(index, 2, self.parsedJSON['pictureData'][index]['date'])
        self.parsedJSON['pictureData'][index]['desc'] = editString
        return
    
    def getPictureAmount(self):
        return self.pictureAmount
    
    def generateThumbs(self, thumbnailSize, generationType):
        index = 0
        thumbPath = self.filepathLocation + "\\thumbs\\"
        
        if not os.path.exists(thumbPath):
            os.makedirs(thumbPath)
        
        for index in range(self.pictureAmount):
            image = Image.open(self.filepathLocation + self.parsedJSON['pictureData'][str(index)]['picURL'])
            width, height = image.size
            if thumbnailSize > height:
                width = round(width * (thumbnailSize / height))
                height = thumbnailSize
                image = image.resize((width, thumbnailSize), 0)
                
            if thumbnailSize > width:
                height = round(height * (thumbnailSize / width))
                width = thumbnailSize
                image = image.resize((thumbnailSize, height), 0)

            if generationType == 0: # Keep aspect ratio, no crop.
                image.thumbnail((thumbnailSize, thumbnailSize))
            elif generationType == 1: # Keep aspect ratio, square cropping.
                if width > height:
                    width = round(width * (thumbnailSize / height))
                    height = thumbnailSize
                    image = image.resize((width, height), 3)
                    left = round((width - thumbnailSize)/2)
                    right = round((width + thumbnailSize)/2)
                    image = image.crop((left, 0, right, thumbnailSize))
                else:
                    height = round(height * (thumbnailSize / width))
                    width = thumbnailSize
                    image = image.resize((width, height), 3)
                    top = round((height - thumbnailSize)/2)
                    bottom = round((height + thumbnailSize)/2)
                    image = image.crop((0, top, thumbnailSize, bottom))
            thumbName = self.parsedJSON['pictureData'][str(index)]['picURL']
            image.save(thumbPath + thumbName, "PNG")
        return
    
    def formatConfiguration(self):
        with open("msge_config.cfg") as tempFile:
            configFile = tempFile.readlines()
        self.allowedFormats = list()
        for line in configFile:
            if not line:
                pass
            else:
                if line[0] == '.':
                    line = line.rstrip()
                    self.allowedFormats.append(line)
        return
    
    def formatParsing(self, filename):
        filetype = '.' + filename.split('.')[-1]
        for type in self.allowedFormats:
            if type == filetype:
                return True
        return False
    
    def imageValidation(self):
        return
    
    def debugGetParsedJSON(self):
        return self.parsedJSON

""" WxWPython class definitions.
"""
# View panel, leftmost panel.
class ViewPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent) # call original constructor
        self.thumbnailImage = wx.Image('./assets/banner.png')
        self.thumbnailImage.Rescale(256, 256, quality=wx.IMAGE_QUALITY_BILINEAR)
        
        self.thumbnailControl = wx.StaticBitmap()
        self.thumbnailControl.Create(self, -1, self.thumbnailImage)
        self.thumbnailControl.SetBackgroundColour('gray')
        
        self.currentFileControl = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.currentFileControl.SetForegroundColour('red')
        self.currentFileControl.Label = "No file loaded."
        
        self.entryListControl = wx.ListBox(self, style=wx.LB_SINGLE)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.thumbnailControl, 2, wx.EXPAND)
        self.mainSizer.Add(self.currentFileControl, 0, wx.EXPAND|wx.TOP, border=4)
        self.mainSizer.Add(self.entryListControl, 3, wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
        self.SetSizer(self.mainSizer)

# Edit panel, rightmost panel.
class EditPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('white')
        
        self.titleLabel = wx.StaticText(self, -1, 'Title')
        self.titleLabel.SetForegroundColour('gray')
        self.titleControl = wx.TextCtrl(self)
        
        self.dateLabel = wx.StaticText(self, -1, 'Date')
        self.dateLabel.SetForegroundColour('gray')
        self.dateControl = wx.TextCtrl(self)
        
        self.descLabel = wx.StaticText(self, -1, 'Description')
        self.descLabel.SetForegroundColour('gray')
        self.descControl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        self.mainSizer = wx.StaticBoxSizer(wx.VERTICAL, self, 'Attributes')
        self.mainSizer.Add(self.titleLabel, 0)
        self.mainSizer.Add(self.titleControl, 0, wx.EXPAND)
        self.mainSizer.Add(self.dateLabel, 0)
        self.mainSizer.Add(self.dateControl, 0, wx.EXPAND)
        self.mainSizer.Add(self.descLabel, 0, wx.TOP, border=4)
        self.mainSizer.Add(self.descControl, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)

# Main window.
class MainWindow(wx.Frame):
    # derive a new class of frame
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,600))
        self.SetBackgroundColour('white')
        self.CreateStatusBar() # status bar in the bottom window
        
        self.gallery = GalleryJSON()
        self.gallery.formatConfiguration()
        self.currentFilepath = None
        self.currentIndex = 0
        self.fileIsLoaded = False
        self.firstClicked = False
        self.metaWindow = MetadataWindow(self)
        
        fileMenu = wx.Menu()
        menuNew = fileMenu.Append(wx.ID_NEW, '&New',  'Create a new .JSON file from a folder of images.')
        menuOpen = fileMenu.Append(wx.ID_OPEN, '&Open',  'Open a .JSON file.')
        fileMenu.AppendSeparator()
        menuSave = fileMenu.Append(wx.ID_SAVE, '&Save',  'Save the currently open .JSON file.')
        fileMenu.AppendSeparator()
        menuExit = fileMenu.Append(wx.ID_EXIT,'&Exit',   'Close the program.')
        
        toolsMenu = wx.Menu()
        menuMetadata = toolsMenu.Append(6661, '&Edit Gallery Metadata',    'Change gallery title, description, and location prefix.')
        menuThumbnail = toolsMenu.Append(6662, '&Generate Thumbnails',    'Generate a folder of thumbnails for use with the gallery.')
        
        helpMenu = wx.Menu()
        menuHelp = helpMenu.Append(wx.ID_ABOUT, '&About',    'Information about this program.')
        
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, '&File') # adding the "fileMenu" to the menuBar
        menuBar.Append(toolsMenu, '&Tools') # adding the "helpMenu" to the menuBar
        menuBar.Append(helpMenu, '&Help') # adding the "helpMenu" to the menuBar
        self.SetMenuBar(menuBar)  # adding the MenuBar to the Frame content
        
        # define panel classes for this frame
        self.frameViewPanel = ViewPanel(self)
        self.frameEditPanel = EditPanel(self)
        
        # put columns in main horizontal sizer
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.frameViewPanel, 1, wx.EXPAND|wx.ALL, border=4)
        self.mainSizer.Add(self.frameEditPanel, 1, wx.EXPAND|wx.ALL, border=4)
        
        # set the frame's sizer with other settings
        self.SetAutoLayout(1)
        self.SetSizer(self.mainSizer)
        
        # define events for menu, buttons, and resize
        self.resized = False # the dirty flag
        self.Bind(wx.EVT_SIZING, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_MENU, self.OnJSONGenerate, menuNew)
        self.Bind(wx.EVT_MENU, self.OnJSONOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnJSONSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnQuit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnMetadataOpen, menuMetadata)
        self.Bind(wx.EVT_MENU, self.OnThumbnailOpen, menuThumbnail)
        self.Bind(wx.EVT_MENU, self.OnAboutOpen, menuHelp)
        self.Bind(wx.EVT_LISTBOX, self.refreshAll, self.frameViewPanel.entryListControl)
        self.Bind(wx.EVT_BUTTON, self.metadataUpdate, self.metaWindow.acceptButton)
        self.Bind(wx.EVT_BUTTON, self.metadataCancel, self.metaWindow.cancelButton)
        
        self.Show(True) # show the frame
    
    def OnJSONGenerate(self, event):
        if self.fileIsLoaded:
            self.JSONClose()
        openDir = wx.DirDialog(self, "Select a folder of images to generate a JSON with.")
        if openDir.ShowModal() == wx.ID_OK:
            self.currentFilepath = openDir.GetPath()
            self.gallery.generateJSON(self.currentFilepath)
            self.populateList()
            self.frameViewPanel.currentFileControl.Label = self.gallery.dirname
            self.fileIsLoaded = True
        else:
            return
    
    def OnJSONOpen(self, event):
        if self.fileIsLoaded:
            self.JSONClose()
        openFile = wx.FileDialog(self, "Select your .JSON file.")
        if openFile.ShowModal() == wx.ID_OK:
            self.currentFilepath = openFile.GetPath()
            self.gallery.openJSON(self.currentFilepath)
            self.populateList()
            self.frameViewPanel.currentFileControl.Label = self.gallery.dirname
            self.fileIsLoaded = True
        else:
            return
    
    def OnJSONSave(self, event):
        if self.fileIsLoaded:
            self.changeTitle()
            self.changeDate()
            self.changeDesc()
            self.gallery.saveJSON()
        else:
            return
    
    def JSONClose(self):
        if self.fileIsLoaded:
            self.frameViewPanel.thumbnailImage = wx.Image('./assets/banner.png')
            self.frameViewPanel.thumbnailControl.SetBitmap(self.frameViewPanel.thumbnailImage)
            self.currentFilepath = None
            self.fileIsLoaded = False
            self.frameViewPanel.entryListControl.Clear()
            self.frameEditPanel.titleControl.Clear()
            self.frameEditPanel.dateControl.Clear()
            self.frameEditPanel.descControl.Clear()
        else:
            return

    def OnMetadataOpen(self, event):
        if self.fileIsLoaded:
            self.metaWindow.titleControl.SetValue(self.gallery.getMetadataTitle())
            self.metaWindow.prefixControl.SetValue(self.gallery.getMetadataPrefix())
            self.metaWindow.descControl.SetValue(self.gallery.getMetadataDesc())
            self.metaWindow.Show()
        else:
            return

    def OnThumbnailOpen(self, event):
        if self.fileIsLoaded:
            self.gallery.generateThumbs(64, 1)
        else:
            return

    def OnAboutOpen(self, event):
        popupWindow = AboutWindow(self)
        popupWindow.Show()
        return
    
    def OnQuit(self, event):
        exit()

    def OnSize(self,event):
        self.resized = True # set dirty
        return

    def OnIdle(self, event):
        if self.resized:
            # take action if the dirty flag is set
            """
            Is our image higher than it is wide?
            If so, scale its height to the max size of the image control.
            Then, properly scale the other dimension.

            Otherwise, do the same but in reverse.
            """       
            self.frameViewPanel.Refresh()
            self.frameEditPanel.Refresh()
            self.resized = False # reset the flag
        return
    
    def OnUndo(self, event):
        if self.fileIsLoaded:
            self.gallery.historyUndo()
        else:
            return
        
    def OnRedo(self, event):
        if self.fileIsLoaded:
            self.gallery.historyRedo()
        else:
            return
        
    def populateList(self):
        for index in range(self.gallery.getPictureAmount()):
            self.frameViewPanel.entryListControl.Insert(self.gallery.getPicURL(str(index)), index)
        return
    
    def refreshAll(self, event):
        if self.fileIsLoaded:
            if self.firstClicked:
                self.changeTitle()
                self.changeDate()
                self.changeDesc()
            self.firstClicked = True
            
            self.currentIndex = str(self.frameViewPanel.entryListControl.GetSelection())
            
            thumbSize = self.frameViewPanel.thumbnailControl.GetSize()
            self.frameViewPanel.thumbnailImage = wx.Image(self.gallery.filepathLocation + self.gallery.getPicURL(self.currentIndex))
            self.frameViewPanel.thumbnailControl.SetBitmap(self.frameViewPanel.thumbnailImage)
            self.frameViewPanel.thumbnailControl.SetSize(thumbSize)
            self.frameEditPanel.titleControl.SetValue(self.gallery.getTitle(self.currentIndex))
            self.frameEditPanel.dateControl.SetValue(self.gallery.getDate(self.currentIndex))
            self.frameEditPanel.descControl.SetLabelMarkup(self.gallery.getDesc(self.currentIndex))
            
            self.frameViewPanel.Refresh()
            self.frameEditPanel.Refresh()
            
            return
        else:
            return
    
    def changeTitle(self):
        if self.fileIsLoaded:
            self.gallery.setTitle(str(self.currentIndex), self.frameEditPanel.titleControl.GetValue())
        else:
            return
    
    def changeDate(self):
        if self.fileIsLoaded:
            self.gallery.setDate(str(self.currentIndex), self.frameEditPanel.dateControl.GetValue())
        else:
            return
        
    def changeDesc(self):
        if self.fileIsLoaded:
            self.gallery.setDesc(str(self.currentIndex), self.frameEditPanel.descControl.GetValue())
        else:
            return

    def metadataUpdate(self, event):
        if self.fileIsLoaded:
            self.gallery.setMetadataTitle(self.metaWindow.titleControl.GetValue())
            self.gallery.setMetadataPrefix(self.metaWindow.prefixControl.GetValue())
            self.gallery.setMetadataDesc(self.metaWindow.descControl.GetValue())
            self.metaWindow.Hide()
        else:
            return
    
    def metadataCancel(self, event):
        self.metaWindow.Hide()

""" Separate popup / tool windows. 
"""
class MetadataWindow(wx.Frame):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.CAPTION ^ wx.RESIZE_BORDER) # call original constructor
        self.SetInitialSize((300, 300))
        self.SetBackgroundColour('white')
        
        self.titleLabel = wx.StaticText(self, -1, 'Gallery Title')
        self.titleLabel.SetForegroundColour('gray')
        self.titleControl = wx.TextCtrl(self)
        
        self.prefixLabel = wx.StaticText(self, -1, 'Gallery File Prefix')
        self.prefixLabel.SetForegroundColour('gray')
        self.prefixControl = wx.TextCtrl(self)
        
        self.descLabel = wx.StaticText(self, -1, 'Gallery Description')
        self.descLabel.SetForegroundColour('gray')
        self.descControl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        self.acceptButton = wx.Button(self, 6663, "Accept")
        self.cancelButton = wx.Button(self, 6664, "Cancel")
        
        self.mainSizer = wx.StaticBoxSizer(wx.VERTICAL, self, 'Metadata')
        self.mainSizer.Add(self.titleLabel, 0)
        self.mainSizer.Add(self.titleControl, 0, wx.EXPAND)
        self.mainSizer.Add(self.prefixLabel, 0)
        self.mainSizer.Add(self.prefixControl, 0, wx.EXPAND)
        self.mainSizer.Add(self.descLabel, 0, wx.TOP, border=4)
        self.mainSizer.Add(self.descControl, 1, wx.EXPAND)
        self.secondSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, "")
        self.mainSizer.Add(self.secondSizer, 0, wx.EXPAND)
        self.secondSizer.Add(self.acceptButton, 0, wx.EXPAND)
        self.secondSizer.Add(self.cancelButton, 0, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        
class AboutWindow(wx.Frame):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER) # call original constructor
        self.SetInitialSize((272, 294))
        self.SetBackgroundColour('black')
        
        self.bannerImage = wx.Image('./assets/banner.png')
        self.bannerControl = wx.StaticBitmap()
        self.bannerControl.Create(self, 0, self.bannerImage)
        
        self.aboutLabel = wx.StaticText(self, -1, 'version 01, finished on 8/16/24')
        self.aboutLabel.SetForegroundColour('white')

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.secondSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.secondSizer.Add(self.aboutLabel, 0, wx.CENTER)
        self.mainSizer.Add(self.bannerControl, 0, wx.CENTER)

def main():
    app = wx.App(False)  # create a new app, don't redirect stdout/stderr to a window
    frame = MainWindow(None, 'mapleshira Static Gallery Editor')
    app.MainLoop()
    return 0

main()