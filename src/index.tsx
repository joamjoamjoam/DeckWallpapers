import {PanelSection, PanelSectionRow, ToggleField, DialogButton, staticClasses, definePlugin, Router, ServerAPI } from "decky-frontend-lib";
import { VFC } from "react";
import { FaShip } from "react-icons/fa";


const Content: VFC<{ serverAPI: ServerAPI; }> = ({serverAPI}) => {
  return (
    <PanelSection title="Settings">
      <PanelSectionRow>
        <ToggleField
          checked={true}
          label={"Enabled:"}
          description={"Show Proton DB Medal on Game Screen"}
          onChange={() => {}}
        />
      </PanelSectionRow>
    </PanelSection>
  );
};

const DeckyPluginRouterTest: VFC = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Router.NavigateToStore()}>
        Go to Store
      </DialogButton>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  serverApi.routerHook.addRoute("/ProtonDBMedals", DeckyPluginRouterTest, {
    exact: true,
  });

  return {
    title: <div className={staticClasses.Title}>ProtonDB Game Badges</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
      serverApi.routerHook.removeRoute("/ProtonDBMedals");
    },
  };
});