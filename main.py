from utilities import Utilities
import time, asyncio, os, json
from injector import inject_to_tab, get_tab, tab_has_element, get_tabs
import logging

pluginManagerUtils = Utilities(None)
Initialized = False
Enabled=False
medalElementID = "protonDBMedalID"


def log(text : str):
    f = open("/tmp/log.txt", "a")
    f.write(text + "\n")
    f.close()

class Plugin:

    protonDBTierColors = {
        "PENDING" : "#363135",
        "BORKED" : "red",
        "BRONZE" : "goldenrod",
        "SILVER" : "silver",
        "GOLD" : "gold",
        "PLATINUM" : "LightGray"
    }

    async def areMedalsEnabled(self):
        global Enabled
        Enabled = (not Enabled)
        return Enabled

    def generateAddMedalJS(self, appID):
        
        # Get Tier from ProtonDB or local Cache (  pending = '#6a6a6a', borked = '#ff0000', bronze = '#cd7f32', silver = '#a6a6a6', gold = '#cfb53b', platinum = '#b4c7dc'
        tier = "GOLD"
        tierBgColor = "dimgrey"
        tierFgColor = "white"
        protonDBAPIURI = f"https://www.protondb.com/api/v1/reports/summaries/{appID}.json"

        # try:
        #     log("Sending request to PDB")
        #     response = pluginManagerUtils.http_request(self, "GET", protonDBAPIURI,  NULL)
        #     log("Done Sending request to PDB")

        #     if response:
        #         json = response["body"]
        #         log(json)
        #         if response["status"] == 200:
        #             #process JSON 
        #             pass
                
        #     else:
        #         log("Cant Access protonDB")
        # except Exception as exc:
        #     log("Error Sending request to PDB: " + str(exc))
        #     tier = "NONE"


        tierBgColor = self.protonDBTierColors[tier]

        if tier != "NONE":
            js = ""
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
                            button.style.backgroundColor = "{tierBgColor}";
                            button.style.color = "rgba(0, 0, 0, 50%)";
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

                        return buttonInjected;
                    }})()
                    """
            else:
                js = ""
        else:
            log("Error Retrieving PDB info.")

            
        return js



    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        #badgeInjected = False

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
                        tabs = await get_tab("SP")
                        try:
                            res = False
                            log("Injecting App Id JS")
                            value = await inject_to_tab("SP", getAppIDJS, False)
                            log(f"value: {value}")
                            if value:
                                appID = value["result"]["result"]["value"]

                                if int(appID) > 0:
                                    log(f"Injecting App Medal ({appID}) JS")
                                    appMedalJS = self.generateAddMedalJS(self, appID)
                                    log(f"medalJS: {appMedalJS}")
                                    value = await inject_to_tab("SP", appMedalJS, False)
                                    log(f"value: {value}")
                                    if value:
                                        res = value["result"]["result"]["value"]
                                        log(f"Result: {res}")
                                    else:
                                        log("Result: FALSE")
                                else:
                                    log("Couldnt find an App ID in URL")
                            else:
                                log("Couldnt find an App ID")




                            log(str(value))
                            
                            log("Was Successful")
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
