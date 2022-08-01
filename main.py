from utilities import Utilities
import time, asyncio, os, json, aiohttp
from injector import inject_to_tab, get_tab, tab_has_element, get_tabs
import logging

pluginManagerUtils = Utilities(None)
Initialized = False
Enabled=False
medalElementID = "protonDBMedalID"
cachePath = os.path.abspath( __file__ )


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
        global Enabled
        Enabled = (not Enabled)
        return Enabled
    
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
                        console.log("Game Needs Button");
                        rv = true;
                    }}
                    else {{
                        console.log("Button Already Existed");
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


    async def generateAddMedalJS(self, appID):
        
        # Get Tier from ProtonDB or local Cache (  pending = '#6a6a6a', borked = '#ff0000', bronze = '#cd7f32', silver = '#a6a6a6', gold = '#cfb53b', platinum = '#b4c7dc'
        tier = "NONE"
        tierBgColor = "black"
        tierFgColor = "0, 0, 0"
        protonDBAPIURI = f"https://www.protondb.com/api/v1/reports/summaries/{appID}.json"
        js = ""
        rv = False

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
            
        tierBgColor = self.protonDBTierColors[tier]
        if tier == "PENDING":
            tierFgColor = "255, 255, 255"
        
        log(f"Genrating medal for ID: {appID}, Tier: {tier}, Color: {tierBgColor}, FG Color RGB: {tierFgColor}")
        if tier != "NONE":
            
            if int(appID) > 0:
                #Generate JavaScript to add medal to Page.
                js = f"""
                    (function() {{
                        buttonInjected = false;
                        // Inject Button Link
                        capsuleList = document.querySelectorAll("[class^=sharedappdetailsheader_TopCapsule]");
                        if(capsuleList){{
                            capsule = capsuleList[0];
                            console.log("Found Capsule Injecting Link");
                            protonDBMedalButton = capsule.querySelector("#{medalElementID}");
                            if(protonDBMedalButton == null) {{
                                console.log("Adding Button");
                                var button = document.createElement("a");
                                button.id = "{medalElementID}";
                                button.href = 'https://www.protondb.com/app/{appID}';

                                button.style.position = "absolute";
                                button.style.top = "24px";
                                button.style.left = "24px";
                                button.style.display = "flex";
                                button.style.alignItems = "center";
                                button.style.padding = "4px 8px";
                                button.style.backgroundColor =  "{tierBgColor}";
                                button.style.color = "rgba({tierFgColor}, 50%)";
                                button.style.fontSize = "20px";
                                button.style.textDecoration = "none";
                                button.style.borderRadius = "4";
                                
                                console.log("Adding Button Image");
                                // Add Image to Button
                                var img = document.createElement("img");
                                img.src = 'https://www.protondb.com/sites/protondb/images/site-logo.svg';
                                img.style.width = "20px";
                                img.style.marginRight = "4px";
                                button.appendChild(img);

                                console.log("Adding Button text");
                                // Add Image Text
                                var spanText = document.createElement("span");
                                spanText.textContent = "{tier}";
                                button.appendChild(spanText);

                                // add the button to the div
                                console.log("Adding Button to capsule");
                                capsule.appendChild(button);
                                buttonInjected = true;
                            }}
                            else {{
                                console.log("Button Already Existed");
                            }}
                        }}

                        return buttonInjected;
                    }})()
                    """

                value = await inject_to_tab("SP", js, False)
                log(f"value: {value}")
                if value:
                    res = value["result"]["result"]["value"]
                    log(f"Result: {res}")
                    rv = res
                else:
                    log("Result: FALSE")
            else:
                js = ""
        else:
            log("Error Retrieving PDB info.")

            
        return rv



    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        badgeInjected = False

        getAppIDJS =  f"""
            (function() {{
                appID = "0";
                console.log('Examining URL: ' + window.location.href);
                appIdRegex = new RegExp('(?<=https:\/\/steamloopback\.host\/routes\/library\/app\/)([0-9]+)');
                matches =  window.location.href.match(appIdRegex);
                if(matches){{
                    appID = matches[0];
                    console.log('Regex ID Matched: ' + appID);      
                }}
                else{{
                    console.log('no Matches found');
                }}
                return appID;
            }})()
            """


        try:
            while True:
                global Initialized
                if Initialized:
                    try:
                        try:
                            res = False
                            log("Injecting App Id JS")
                            value = await inject_to_tab("SP", getAppIDJS, False)
                            log(f"value: {value}")
                            if value:
                                appID = value["result"]["result"]["value"]
                                if int(appID) > 0 and int(appID) < int('0x02000000', 16): # handle non steam IDs
                                    if not badgeInjected:
                                        addButton = await self.gameNeedsButton(self)
                                        if addButton:
                                            log(f"Generating Button for game ({appID})")
                                            rv = await self.generateAddMedalJS(self, appID)

                                            if rv:
                                                log("Button Was Added. Setting Needs Generate Button to False")
                                                badgeInjected = True
                                            else:
                                                log("Error Adding Button.")
                                        else:
                                            log("Button Was not Needed.")
                                            badgeInjected = True
                                else:
                                    log("No AppID or not Game Screen or is a Non-Steam Game")
                                    badgeInjected = False
                            else:
                                log("Couldnt find an App ID. Setting Generate Button to True")
                                badgeInjected = False
                        except Exception as e:
                            log("Failed: " + str(e))

                    except:
                        log("SP Tab Not Available")
                else:
                    try:
                        os.remove("/tmp/log.txt")
                    except:
                        pass
                    Initialized = True
                    log("Initialized Main")
                log("Sleeping 2")
                await asyncio.sleep(2)
        except Exception as e:
            log("Fatal Error Exiting" + str(e))
