import {PanelSection, PanelSectionRow, ToggleField, staticClasses, definePlugin, ServerAPI } from "decky-frontend-lib";
import { VFC } from "react";
import { FaShip } from "react-icons/fa";
import * as python from "./python";


const Content: VFC<{ serverAPI: ServerAPI; }> = ({serverAPI}) => {

  var medalsEnabled = false;
  python.setServer(serverAPI);

  python.resolve(python.getMedalsEnabled(), medalsEnabled);

  return (
    <PanelSection title="Settings">
      <PanelSectionRow>
        <ToggleField
          checked={medalsEnabled}
          label={"Enabled:"}
          description={"Show Proton DB Medal on Game Screen"}
          onChange={(medalsEnabled: boolean) => {
            console.log("SMT is now " + medalsEnabled.toString());
            python.execute(python.setMedalsEnabled(medalsEnabled))
          }}
        />
      </PanelSectionRow>
    </PanelSection>
  );
};


export default definePlugin((serverApi: ServerAPI) => {

  return {
    title: <div className={staticClasses.Title}>ProtonDB Game Badges</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
      
    },
  };
});