import {PanelSection, PanelSectionRow, ButtonItem, staticClasses, definePlugin, ServerAPI, showModal, ModalRoot, Field } from "decky-frontend-lib";
import { VFC } from "react";
import { FaShip } from "react-icons/fa";
import * as python from "./python";

 // returns function passed for convenience
// later, to unpatch


const Content: VFC<{ serverAPI: ServerAPI; }> = ({}) => {

  return (
    <PanelSection title="Settings">
      <PanelSectionRow>
        <ButtonItem
            layout="below"
            onClick={(e) => {
              var elem = e.currentTarget as HTMLButtonElement;
              console.log(e.currentTarget)
              elem.disabled = true
              python.resolve(python.hasCSSLoader(), (hasCSSLoader: boolean) => {
                console.log("Got CSS Loaer State: " + String(hasCSSLoader))
                if (hasCSSLoader) {
                  showModal(<ModalRoot
                      onOK={async () => {
                        python.execute(python.parseExtensionsForThemes())
                      }}
                      onCancel={async () => {
                      }}
                    >
                      <div className={staticClasses.Title} style={{ flexDirection: 'column' }}>
                      <h3>Adding Images to Wallpaper CSS Loader Theme. Reload Themes in CSSLoader.</h3>
                      </div>
                  </ModalRoot>
                  )
                }
                else{
                  showModal(<ModalRoot
                      onOK={async () => {
                      }}
                      onCancel={async () => {
                      }}
                    >
                      <div className={staticClasses.Title} style={{ flexDirection: 'column' }}>
                      <h3>CSS Loader is Required. Pleae Install CSS Loader First.</h3>
                      </div>
                  </ModalRoot>
                  )
                }
                elem.disabled = false
            })
            
            }
          }
          >
            Add/Update Wallpaper Theme to CSSLoader
          </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <Field
          label={"How to Use"}
          description={
            <div><ol>
              <li>Install CSS Loader if it's not Already Installed.</li>
              <li>Load Images into /home/deck/wallpaperImages.</li>
              <li>Click the Add/Update Images button</li>
              <li>Reload Themes in CSS Loader</li>
              <li>Enable The "Wallpapers" theme and select your backgrounds.</li>
            </ol></div>
          }
        ></Field>
      </PanelSectionRow>
    </PanelSection>
  );
};


export default definePlugin((serverApi: ServerAPI) => {
  
  python.setServer(serverApi);
  return {
    title: <div className={staticClasses.Title}>Wallpapers</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
      console.log("Dismounting");
    },
  };
});