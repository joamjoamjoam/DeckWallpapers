import os, json, shutil, re, base64
#from injector import inject_to_tab, get_tab, tab_has_element, get_tabs
import logging

Initialized = False
themeName = "Wallpapers2"
themeFolder = "/home/deck/homebrew/themes"
symLinkToHostDir = "/home/deck/.local/share/Steam/steamui/themes_custom"
themeBaseFolder = f"/home/deck/homebrew/themes/{themeName}"
imagesFolder = "/home/deck/wallpaperImages"
cssDir = "generatedCSSFiles"
b64Dir = "sharedB64Images"
fallbackCSSDir = "fallbackCSS"
themeTemplateFileName = "themeTemplate.json"
autoGenHeader = "/* This File was Auto-Generated Do Not Modify */\n\n"
cssVariableTemplate = f"{autoGenHeader}:root{{\n\t--<customVarName>: var(--<imageVariableName>, radial-gradient(155.42% 100% at 0% 0%, #151f25 0 0%, #152533 100%));\n}}"
fallbackCssVariableTemplate = f"{autoGenHeader}:root{{\n\t--<customVarName>: radial-gradient(155.42% 100% at 0% 0%, #151f25 0 0%, #152533 100%) !important;\n}}"
validExtensions = [".jpg", ".png", ".svg", ".gif", ".jpeg"]

cssFileTypes = { 
    b64Dir: f"{autoGenHeader}:root{{\n\t--<imageVariableName>: <fileURL> !important;\n}}",
    fallbackCSSDir: fallbackCssVariableTemplate
}

imageCount = 0

def log(text : str):
    try:
        f = open(f"/home/deck/homebrew/plugins/Wallpapers/log.txt", "a")
        f.write(text + "\n")
        f.close()
    except:
        pass

#### Helper Functions

def getURLforFile(file):

    fileURL = ""

    file = os.path.basename(file)

    if os.path.exists(symLinkToHostDir):
        log("Sym Link is here")
        fileURL = f"url('/themes_custom/{themeName}/images/{file}')"
    else:
        # fall back to b64
        log("Sym Link not here")
        fileURL = "url('data:image/<imgType>;base64,<b64String>')"

        fileURL = fileURL.replace("<imgType>", getImgTypeTagForFile(file)).replace("<b64String>", getB64ForFile(file))

    return fileURL

def getB64ForFile(file):
    rv = ""
    try:
        if os.path.exists(file):
            with open(file, "rb") as image_file:
                raw = base64.b64encode(image_file.read())
                rv = raw.decode('utf-8')
    except:
        pass
    
    return rv

def getImgTypeTagForFile(file):
    rv = "jpeg"

    fileInfo = os.path.splitext(file)

    if len(fileInfo) == 2:
        fileExt = fileInfo[1].lower()

        if fileExt in validExtensions:
            if fileExt == ".jpg" or fileExt == ".jpeg":
                rv = "jpeg"
            elif fileExt == ".svg":
                rv = "svg+xml"
            elif fileExt == ".gif":
                rv = "gif"
            elif fileExt == ".png":
                rv = "png" 

        else:
            rv = "jpeg"

    return rv

def writeCSSType(type, filePath, varName):

    rv = True

    fileInfo = os.path.splitext(os.path.basename(filePath))
    try:
        if not type in cssFileTypes.keys() or len(fileInfo) != 2:
            raise ValueError("Not a Valid type or image path") 
        
        fileName = f"{varName}.css"
        
        variableName = "WPRImage" + varName.replace(" ", "")

        if type == b64Dir:
            f = open(f"{cssDir}/{type}/{fileName}" , "w")
            tmpStr = cssFileTypes[type].replace("<imageVariableName>", variableName).replace("<fileURL>", getURLforFile(filePath))
            f.write(tmpStr)
            f.close()
        elif type == fallbackCSSDir:
            f = open(f"{cssDir}/{type}/{fileName}" , "w")
            tmpStr = cssFileTypes[type].replace("<customVarName>", varName)
            f.write(tmpStr)
            f.close()
        else:
            f = open(f"{cssDir}/{type}/{fileName}" , "w")
            f.write(cssFileTypes[type].replace("<imageVariableName>", variableName))
            f.close()
    except Exception as e:
        log(f"Error  writing type {type}: {str(e)}")
        rv = False

    return rv


def copyThemeTemplate(srcDir, destDir):
    for file in os.listdir(srcDir):
        trueSrcFilePath = f"{srcDir}/{file}"
        trueDestFilePath = f"{destDir}/{file}"


        if file in ["images"]:
            # Symbolicly Link images to imageFolder
            if not os.path.exists(f"{destDir}/images"):
                os.system(f"ln -s {imagesFolder} {destDir}/images")
        else:
            if os.path.isdir(trueSrcFilePath):
                if os.path.isdir(trueDestFilePath):
                    shutil.rmtree(trueDestFilePath)
                
                shutil.copytree(trueSrcFilePath, trueDestFilePath)  
            else:
                shutil.copy2(trueSrcFilePath, trueDestFilePath)


def addThemeThemeAtPath(path):
    if os.path.isdir(path) and os.path.isdir(imagesFolder):
        os.chdir(path)
        global imageCount
         # Copy Template to Folder

        copyThemeTemplate((os.path.dirname(os.path.realpath(__file__)) + "/WallpapersTemplate"), path)

        if os.path.isdir(cssDir):
            shutil.rmtree(cssDir)
        
        jsonTemplate = open(f"{themeTemplateFileName}")
        themeJson = json.load(jsonTemplate)
        jsonTemplate.close()
        # Create Folder Structure
        os.mkdir(cssDir)
        os.mkdir(f"{cssDir}/{b64Dir}")
        os.mkdir(f"{cssDir}/{fallbackCSSDir}")

        for k,v in themeJson["patches"].items():
            if v["type"] == "dropdown-image":
                if "css_variable" in v.keys() and re.match(r"[A-Za-z0-9_-]+", v["css_variable"]):
                    tmpVar = v["css_variable"]
                    log(tmpVar)
                    os.mkdir(f'{cssDir}/{tmpVar}')
                    cssFileTypes[v["css_variable"]] = cssVariableTemplate.replace("<customVarName>", v["css_variable"])

                    if "values" in v.keys():
                        v["values"]["None"] = {f"{fallbackCSSDir}/{v['css_variable']}.css": ["SP"]}
                        writeCSSType(fallbackCSSDir, "", v['css_variable'])
                    if "default" in v.keys() and "None" != v["default"]:
                        v["default"] = "None"

                else:
                    raise ValueError(f'Invalid css variable name')




        for root, dirs, files in os.walk(f"{path}/images"):
            for file in files:
                fileInfo = os.path.splitext(file)
                if len(fileInfo) == 2 and ((fileInfo[1].lower()) in validExtensions):
                    log("Creating CSS files for " + file)
                    imageImportedSuccessfully = True
                    imageVarName = ""
                    imageVarName = imageVarName.join(e for e in fileInfo[0].lower().title() if (e.isalnum() or e.isspace()))
                    imageVarName = " ".join(imageVarName.split())
                    
                    for cssType, cssTemplate in cssFileTypes.items():
                        if  imageImportedSuccessfully:
                            if cssType != fallbackCSSDir:
                                imageImportedSuccessfully = writeCSSType(cssType, os.path.join(root, file), imageVarName)
                    
                    if imageImportedSuccessfully:
                        # Update Theme.json
                        log("Success")
                        for k,v in themeJson["patches"].items():
                            if v["type"] == "dropdown-image":
                                log(f"Adding {imageVarName} for var {v['css_variable']}")
                                if "css_variable" in v.keys() and re.match(r"[A-Za-z0-9_-]+", v["css_variable"]):
                                    themeJson["patches"][k]["values"][imageVarName] = { f"{cssDir}/{b64Dir}/{imageVarName}.css": ["SP"], f'{cssDir}/{v["css_variable"]}/{imageVarName}.css': ["SP"]}
                                else:
                                    # No Var replace Normal dropdown Patch
                                    v["type"] = "dropdown"
                        imageCount += 1

                        
                    else:
                        log("Failed")

        # Sanitize Extended Types
        for k,v in themeJson["patches"].items():
            if "css_variable" in v.keys():
                del v["css_variable"]
                if "values" in v.keys():
                    v["values"]["None"] = { }
            if "type" in v.keys() and v["type"] == "dropdown-image":
                v["type"] = "dropdown"


        f = open(f"{path}/theme.json" , "w")
        f.write(json.dumps(themeJson, indent=4))
        f.close()
    else:
        log(f"Error Processing Theme at path {path}")


def getExtendedThemesList():
    rv = []
    root = themeFolder

    for file in os.listdir(root):
        if os.path.isdir(F"{root}/{file}"):
            if themeTemplateFileName in os.listdir(f"{root}/{file}"):
                rv.append(f"{root}/{file}")

    return rv

##################################################################################



class Plugin:


    async def isCSSLoaderInstalled(self):
        return os.path.exists("/home/deck/homebrew/themes")

    async def parseExtensionsForThemes(self):
        # Handle Updates by backing up images and wiping template (get version from json)
        log("Parsing theme")
        if not os.path.exists(imagesFolder):
            log("Initialized images Folder")
            os.mkdir(imagesFolder)

        if os.path.isdir(themeFolder):
            if not os.path.isdir(themeBaseFolder):
                os.mkdir(themeBaseFolder)
            
            log("Theme Directory")
            
            addThemeThemeAtPath(themeBaseFolder)
        else:
            log("No Theme Directory")

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        global Initialized
        if not Initialized:
            Initialized = True
            log("Initializing")
            if not os.path.exists(imagesFolder):
                log("Initialized Directory")
                os.mkdir(imagesFolder)
        else:
            return
