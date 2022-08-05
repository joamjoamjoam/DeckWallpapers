import {PanelSection, PanelSectionRow, ToggleField, staticClasses, definePlugin, ServerAPI } from "decky-frontend-lib";
import { VFC } from "react";
import { FaShip } from "react-icons/fa";
import * as python from "./python";
import pdbSiteLogo  from "./../assets/pdbsitelogo.svg";

 // returns function passed for convenience
// later, to unpatch




const Content: VFC<{ serverAPI: ServerAPI; }> = ({serverAPI}) => {

  var medalsEnabled = false;
  python.setServer(serverAPI);

  const setMedalsEnabledFlag = (value: boolean) => {
    medalsEnabled = value;
  };

  python.resolve(python.getMedalsEnabled(), setMedalsEnabledFlag);

  return (
    <PanelSection title="Settings">
      <PanelSectionRow>
        <ToggleField
          checked={medalsEnabled}
          label={"Enabled:"}
          description={"Show Proton DB Medal on Game Screen"}
          onChange={(medalsEnabled: boolean) => {
            console.log("MedalsEnabled is now " + medalsEnabled.toString());
            python.execute(python.setMedalsEnabled(medalsEnabled))
          }}
        />
      </PanelSectionRow>
    </PanelSection>
  );
};


export default definePlugin((serverApi: ServerAPI) => {
  console.log("Patching");
  const patch = serverApi.routerHook.addPatch("/library/app/:appid", (props) => {
    console.log(props);
    console.log(props.children.type);
    
    var tier = "NONE";
    //const { appid: appId } = useParams();
    const appId = location.pathname.split('/').pop();
    console.log();
    python.setServer(serverApi);

    console.log("Getting Tier for AppId " + appId + " ...");

    const setPDBTier = (value: string) => {
      console.log("Got Tier from promise" + value);
      tier = value;

      console.log("Got Tier for AppId " + appId + ": " + tier);
      // Trent Add Back Styles

      const linkStyle : React.CSSProperties = 
      {
        position: "absolute",
        top: "24px",
        left: "24px",
        display: "flex",
        alignItems: "center",
        padding: "4px 8px",
        backgroundColor: "lightgray",
        color: "white",
        fontSize: "20px",
        textDecoration: "none"
      }

      const imgStyle: React.CSSProperties = {
        width: "20px",
        marginRight: "4px",
      }


      var pdbUrl = "https://www.protondb.com/app/" + appId;
      const TestComponent = () => <a id="protonDBMedalID" href={pdbUrl} style={linkStyle}><img id="protonDBMedalPicID" src={pdbSiteLogo} style={imgStyle}></img> <span>{tier}</span></a>
      const oldChildren = props.children;
      console.log("Adding Medal");
      props.children = <>
        <TestComponent/>
        {oldChildren}
      </>
    };

  python.resolve(python.getProtonDBTierForAppId(appId!), setPDBTier);

    
    return props;
  });

  

  return {
    title: <div className={staticClasses.Title}>ProtonDB Game Badges</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
      console.log("Dismounting");
      serverApi.routerHook.removePatch("/library/app/:appid", patch)
    },
  };
});