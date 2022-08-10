from utilities import Utilities
import time, asyncio, os, json, aiohttp
from injector import inject_to_tab, get_tab, tab_has_element, get_tabs
import logging

pluginManagerUtils = Utilities(None)
Initialized = False
medalsEnabled=False
medalElementID = "protonDBMedalID"
configPath = "/home/deck/Documents/protonDBPluginConfig.cfg"


def loadConfig():
    global medalsEnabled
    if os.access(configPath, os.R_OK):
        try:
            file = open(configPath,mode='r')
            configJson = json.loads(file.read())
            medalsEnabled = configJson["medalsEnabled"]
            log(f"Medals Enabled Loaded as {medalsEnabled}")
        except:
            medalsEnabled = False
    else:
        medalsEnabled = False

    
def saveConfig():
    global medalsEnabled
    file = open(configPath,"w")
    try:
        configJson = {}
        configJson["medalsEnabled"] = medalsEnabled

        configString = json.dumps(configJson)
        log(f"Medals Enabled Saved as {configString}")
        file.write(configString)
        file.close()
    except:
        medalsEnabled = False

def log(text : str):
    pass
    #f = open("/tmp/log.txt", "a")
    #f.write(text + "\n")
    #f.close()


class Plugin:

    protonDBTierColors = {
        "PENDING" : "#363135",
        "BORKED" : "red",
        "BRONZE" : "goldenrod",
        "SILVER" : "silver",
        "GOLD" : "gold",
        "PLATINUM" : "LightGray",
        "NONE" : "black"
    }

    async def areMedalsEnabled(self):
        global medalsEnabled
        return medalsEnabled
    
    async def setMedalsEnabled(self, enableMedals):
        global medalsEnabled
        medalsEnabled = enableMedals
        saveConfig()
    

    async def getProtonDBTierForAppId(self, appID):
        
        # Get Tier from ProtonDB or local Cache (  pending = '#6a6a6a', borked = '#ff0000', bronze = '#cd7f32', silver = '#a6a6a6', gold = '#cfb53b', platinum = '#b4c7dc'
        tier = "NONE"
        protonDBAPIURI = f"https://www.protondb.com/api/v1/reports/summaries/{appID}.json"

        log("Getting Tier for appid " + appID + ": " + protonDBAPIURI)
        try:
            log("Cant Access protonDB")
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession() as session:
                async with session.get(protonDBAPIURI, timeout=timeout, ssl=False) as resp:
                    responseBody = await resp.text()
                    log(f"Retrieved data({resp.status}): {responseBody}")
                    if resp.status == 200:
                        responseBody = json.loads(responseBody)
                        tier = str(responseBody["tier"]).upper()
                    elif resp.status == 404:
                        # Default to PENDING if the request is otherwise good.
                        tier = "PENDING"
                    else:
                        log(f"Proton DB Access Error ({resp.status})")
                    
                    
        except Exception as exc:
            tier = "NONE"
            log(f"Error retrieving PDB Info: " + str(exc))
        
        log(f"Genrating medal for ID: {appID}, Tier: {tier}")

        return tier

    
    async def gameNeedsButton(self):

        rv = False

        js = f"""
            (function() {{
                rv = false;
                // Inject Button Link
                capsuleList = document.querySelectorAll("[class^=sharedappdetailsheader_TopCapsule]");
                if(capsuleList){{
                    capsule = capsuleList[0];
                    protonDBMedalButton = capsule.querySelector("#{medalElementID}");
                    if(protonDBMedalButton == null) {{
                        //console.log("Game Needs Button");
                        rv = true;
                    }}
                    else {{
                        //console.log("Button Already Existed");
                        rv = false
                    }}
                }}

                return rv;
            }})()
            """
        
        value = await inject_to_tab("SP", js, False)
        log(f"gameNeedsButton Injection Result: {value}")

        try:
            rv = value["result"]["result"]["value"]
        except:
            rv = False


        return rv


    # async def generateAddMedalJS(self, appID):
        
    #     # Get Tier from ProtonDB or local Cache (  pending = '#6a6a6a', borked = '#ff0000', bronze = '#cd7f32', silver = '#a6a6a6', gold = '#cfb53b', platinum = '#b4c7dc'
    #     tier = "NONE"
    #     tierBgColor = "black"
    #     tierFgColor = "0, 0, 0"
    #     protonDBAPIURI = f"https://www.protondb.com/api/v1/reports/summaries/{appID}.json"
    #     js = ""
    #     rv = False

    #     try:
    #         log("Cant Access protonDB")
    #         timeout = aiohttp.ClientTimeout(total=3)
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(protonDBAPIURI, timeout=timeout, ssl=False) as resp:
    #                 responseBody = await resp.text()
    #                 log(f"Retrieved data({resp.status}): {responseBody}")
    #                 if resp.status == 200:
    #                     responseBody = json.loads(responseBody)
    #                     tier = str(responseBody["tier"]).upper()
    #                 elif resp.status == 404:
    #                     # Default to PENDING if the request is otherwise good.
    #                     tier = "PENDING"
    #                 else:
    #                     log(f"Proton DB Access Error ({resp.status})")
                    
                    
    #     except Exception as exc:
    #         tier = "NONE"
    #         log(f"Error retrieving PDB Info: " + str(exc))
            
    #     tierBgColor = self.protonDBTierColors[tier]
    #     if tier == "PENDING":
    #         tierFgColor = "255, 255, 255"
        
    #     log(f"Genrating medal for ID: {appID}, Tier: {tier}, Color: {tierBgColor}, FG Color RGB: {tierFgColor}")
    #     if tier != "NONE":
            
    #         if int(appID) > 0:
    #             #Generate JavaScript to add medal to Page.
    #             js = f"""
    #                 (function() {{
    #                     buttonInjected = false;
    #                     // Inject Button Link
    #                     capsuleList = document.querySelectorAll("[class^=sharedappdetailsheader_TopCapsule]");
    #                     if(capsuleList){{
    #                         capsule = capsuleList[0];
    #                         //console.log("Found Capsule Injecting Link");
    #                         protonDBMedalButton = capsule.querySelector("#{medalElementID}");
    #                         if(protonDBMedalButton == null) {{
    #                             //console.log("Adding Button");
    #                             var button = document.createElement("a");
    #                             button.id = "{medalElementID}";
    #                             button.href = 'https://www.protondb.com/app/{appID}';

    #                             button.style.position = "absolute";
    #                             button.style.top = "24px";
    #                             button.style.left = "24px";
    #                             button.style.display = "flex";
    #                             button.style.alignItems = "center";
    #                             button.style.padding = "4px 8px";
    #                             button.style.backgroundColor =  "{tierBgColor}";
    #                             button.style.color = "rgba({tierFgColor}, 50%)";
    #                             button.style.fontSize = "20px";
    #                             button.style.textDecoration = "none";
    #                             button.style.borderRadius = "4";
                                
    #                             //console.log("Adding Button Image");
    #                             // Add Image to Button
    #                             var img = document.createElement("img");
    #                             img.src = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDIyLjEuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4iICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPgo8c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkxheWVyXzJfMV8iIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4IgoJIHZpZXdCb3g9IjAgMCA0OTEgNDkxIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCA0OTEgNDkxOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+CjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+Cgkuc3Qwe2ZpbGw6IzFBMjIzMzt9Cgkuc3Qxe2ZpbGw6I0Y1MDA1Nzt9Cgkuc3Qye2ZpbGw6I0ZGRkZGRjt9Cjwvc3R5bGU+CjwhLS0gPHBhdGggY2xhc3M9InN0MCIgZD0iTTQ1NS4zLDQ5MUgzNS43QzE2LDQ5MSwwLDQ3NSwwLDQ1NS4zVjM1LjdDMCwxNiwxNiwwLDM1LjcsMGg0MTkuN0M0NzUsMCw0OTEsMTYsNDkxLDM1Ljd2NDE5LjcKCUM0OTEsNDc1LDQ3NSw0OTEsNDU1LjMsNDkxeiIvPiAtLT4KPGc+Cgk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNNDcwLjUsMjQ1LjVjMC0yOS44LTM3LjMtNTguMS05NC42LTc1LjZjMTMuMi01OC4zLDcuMy0xMDQuNy0xOC41LTExOS42Yy02LTMuNS0xMi45LTUuMS0yMC41LTUuMXYyMC41CgkJYzQuMiwwLDcuNiwwLjgsMTAuNSwyLjRjMTIuNSw3LjIsMTcuOSwzNC40LDEzLjcsNjkuNGMtMSw4LjYtMi43LDE3LjctNC43LDI3Yy0xOC00LjQtMzcuNi03LjgtNTguMi0xMAoJCWMtMTIuNC0xNy0yNS4yLTMyLjQtMzguMi00NS45YzI5LjktMjcuOCw1OC00Myw3Ny00M1Y0NS4xbDAsMGMtMjUuMiwwLTU4LjIsMTgtOTEuNiw0OS4yYy0zMy40LTMxLTY2LjQtNDguOC05MS42LTQ4Ljh2MjAuNQoJCWMxOSwwLDQ3LjEsMTUuMSw3Nyw0Mi43Yy0xMi44LDEzLjUtMjUuNywyOC44LTM3LjksNDUuOGMtMjAuNywyLjItNDAuNCw1LjYtNTguMywxMC4xYy0yLjEtOS4yLTMuNy0xOC4xLTQuOC0yNi42CgkJYy00LjMtMzUsMS02Mi4zLDEzLjQtNjkuNWMyLjgtMS43LDYuMy0yLjQsMTAuNS0yLjRWNDUuNmwwLDBjLTcuNywwLTE0LjcsMS43LTIwLjcsNS4xYy0yNS44LDE0LjktMzEuNiw2MS4yLTE4LjMsMTE5LjMKCQljLTU3LjEsMTcuNi05NC4yLDQ1LjgtOTQuMiw3NS41YzAsMjkuOCwzNy4zLDU4LjEsOTQuNiw3NS42Yy0xMy4yLDU4LjMtNy4zLDEwNC43LDE4LjUsMTE5LjZjNiwzLjUsMTIuOSw1LjEsMjAuNiw1LjEKCQljMjUuMiwwLDU4LjItMTgsOTEuNi00OS4yYzMzLjQsMzEsNjYuNCw0OC44LDkxLjYsNDguOGM3LjcsMCwxNC43LTEuNywyMC43LTUuMWMyNS44LTE0LjksMzEuNi02MS4yLDE4LjMtMTE5LjMKCQlDNDMzLjQsMzAzLjUsNDcwLjUsMjc1LjMsNDcwLjUsMjQ1LjV6IE0zNTEuMSwxODQuNGMtMy40LDExLjgtNy42LDI0LTEyLjQsMzYuMmMtMy44LTcuMy03LjctMTQuNy0xMi0yMgoJCWMtNC4yLTcuMy04LjctMTQuNS0xMy4yLTIxLjVDMzI2LjUsMTc5LDMzOS4xLDE4MS40LDM1MS4xLDE4NC40eiBNMzA5LjEsMjgyLjFjLTcuMiwxMi40LTE0LjUsMjQuMS0yMi4xLDM1CgkJYy0xMy43LDEuMi0yNy41LDEuOC00MS41LDEuOGMtMTMuOSwwLTI3LjctMC42LTQxLjMtMS43Yy03LjYtMTAuOS0xNS0yMi42LTIyLjItMzQuOWMtNy0xMi0xMy4zLTI0LjItMTkuMS0zNi41CgkJYzUuNy0xMi4zLDEyLjEtMjQuNiwxOS0zNi42YzcuMi0xMi40LDE0LjUtMjQuMSwyMi4xLTM1YzEzLjctMS4yLDI3LjUtMS44LDQxLjUtMS44YzEzLjksMCwyNy43LDAuNiw0MS4zLDEuNwoJCWM3LjYsMTAuOSwxNSwyMi42LDIyLjIsMzQuOWM3LDEyLDEzLjMsMjQuMiwxOS4xLDM2LjVDMzIyLjMsMjU3LjcsMzE1LjksMjcwLDMwOS4xLDI4Mi4xeiBNMzM4LjcsMjcwLjFjNSwxMi4zLDkuMiwyNC42LDEyLjcsMzYuNQoJCWMtMTIsMi45LTI0LjcsNS40LTM3LjgsNy4zYzQuNS03LjEsOS0xNC4zLDEzLjItMjEuN0MzMzEsMjg0LjksMzM0LjksMjc3LjUsMzM4LjcsMjcwLjF6IE0yNDUuNywzNjhjLTguNS04LjgtMTcuMS0xOC42LTI1LjUtMjkuNAoJCWM4LjMsMC40LDE2LjcsMC42LDI1LjIsMC42YzguNiwwLDE3LjItMC4yLDI1LjUtMC42QzI2Mi43LDM0OS40LDI1NC4xLDM1OS4yLDI0NS43LDM2OHogTTE3Ny40LDMxNGMtMTMtMS45LTI1LjYtNC4zLTM3LjYtNy4yCgkJYzMuNC0xMS44LDcuNi0yNCwxMi40LTM2LjJjMy44LDcuMyw3LjcsMTQuNywxMiwyMkMxNjguNSwyOTkuOCwxNzIuOSwzMDcsMTc3LjQsMzE0eiBNMjQ1LjIsMTIzLjFjOC41LDguOCwxNy4xLDE4LjYsMjUuNSwyOS40CgkJYy04LjMtMC40LTE2LjctMC42LTI1LjItMC42Yy04LjYsMC0xNy4yLDAuMi0yNS41LDAuNkMyMjguMywxNDEuNywyMzYuOCwxMzEuOSwyNDUuMiwxMjMuMXogTTE3Ny4zLDE3Ny4xCgkJYy00LjUsNy4xLTksMTQuMy0xMy4yLDIxLjdjLTQuMiw3LjMtOC4yLDE0LjctMTEuOSwyMmMtNS0xMi4zLTkuMi0yNC42LTEyLjctMzYuNUMxNTEuNiwxODEuNSwxNjQuMiwxNzksMTc3LjMsMTc3LjF6IE05NC4zLDI5MgoJCWMtMzIuNS0xMy45LTUzLjUtMzItNTMuNS00Ni40YzAtMTQuNCwyMS0zMi43LDUzLjUtNDYuNGM3LjktMy40LDE2LjUtNi40LDI1LjQtOS4zYzUuMiwxOCwxMi4xLDM2LjcsMjAuNiw1NS45CgkJYy04LjQsMTkuMS0xNS4yLDM3LjctMjAuNCw1NS42QzExMC45LDI5OC41LDEwMi4zLDI5NS40LDk0LjMsMjkyeiBNMTQzLjcsNDIzYy0xMi41LTcuMi0xNy45LTM0LjQtMTMuNy02OS40CgkJYzEtOC42LDIuNy0xNy43LDQuNy0yN2MxOCw0LjQsMzcuNiw3LjgsNTguMiwxMGMxMi40LDE3LDI1LjIsMzIuNCwzOC4yLDQ1LjljLTI5LjksMjcuOC01OCw0My03Nyw0MwoJCUMxNDkuOSw0MjUuNCwxNDYuNCw0MjQuNiwxNDMuNyw0MjN6IE0zNjEuMywzNTMuMWM0LjMsMzUtMSw2Mi4zLTEzLjQsNjkuNWMtMi44LDEuNy02LjMsMi40LTEwLjUsMi40Yy0xOSwwLTQ3LjEtMTUuMS03Ny00Mi43CgkJYzEyLjgtMTMuNSwyNS43LTI4LjgsMzcuOS00NS44YzIwLjctMi4yLDQwLjQtNS42LDU4LjMtMTAuMUMzNTguNiwzMzUuNywzNjAuMiwzNDQuNiwzNjEuMywzNTMuMXogTTM5Ni42LDI5MgoJCWMtNy45LDMuNC0xNi41LDYuNC0yNS40LDkuM2MtNS4yLTE4LTEyLjEtMzYuNy0yMC42LTU1LjljOC40LTE5LjEsMTUuMi0zNy43LDIwLjQtNTUuNmM5LjEsMi44LDE3LjcsNiwyNS44LDkuNAoJCWMzMi41LDEzLjksNTMuNSwzMiw1My41LDQ2LjRDNDUwLDI1OS45LDQyOSwyNzguMiwzOTYuNiwyOTJ6Ii8+Cgk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMTUzLjYsNDUuNUwxNTMuNiw0NS41TDE1My42LDQ1LjV6Ii8+Cgk8Y2lyY2xlIGNsYXNzPSJzdDIiIGN4PSIyNDUuNCIgY3k9IjI0NS41IiByPSI0MS45Ii8+Cgk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMzM2LjgsNDUuMkwzMzYuOCw0NS4yTDMzNi44LDQ1LjJ6Ii8+CjwvZz4KPC9zdmc+Cg=='
    #                             img.style.width = "20px";
    #                             img.style.marginRight = "4px";
    #                             button.appendChild(img);

    #                             //console.log("Adding Button text");
    #                             // Add Image Text
    #                             var spanText = document.createElement("span");
    #                             spanText.textContent = "{tier}";
    #                             button.appendChild(spanText);

    #                             // add the button to the div
    #                             //console.log("Adding Button to capsule");
    #                             capsule.appendChild(button);
    #                             buttonInjected = true;
    #                         }}
    #                         else {{
    #                             //console.log("Button Already Existed");
    #                         }}
    #                     }}

    #                     return buttonInjected;
    #                 }})()
    #                 """

    #             value = await inject_to_tab("SP", js, False)
    #             log(f"value: {value}")
    #             if value:
    #                 res = value["result"]["result"]["value"]
    #                 log(f"Result: {res}")
    #                 rv = res
    #             else:
    #                 log("Result: FALSE")
    #         else:
    #             js = ""
    #     else:
    #         log("Error Retrieving PDB info.")

            
    #     return rv



    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        global medalsEnabled
        badgeInjected = False
        try:
            os.remove("/tmp/log.txt")
            loadConfig()
            log("Initialized Main")
        except Exception as e:
            log("Fatal Error Exiting" + str(e))
