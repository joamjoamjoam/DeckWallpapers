import { ServerAPI } from "decky-frontend-lib";

var server: ServerAPI | undefined = undefined;

export function resolve(promise: Promise<any>, setter: any) {
    (async function () {
        let data = await promise;
        if (data.success) {
            console.debug("Got resolved", data, "promise", promise);
            setter(data.result);
        } else {
            console.warn("Resolve failed:", data, "promise", promise);
        }
    })();
}

export function execute(promise: Promise<any>) {
    (async function () {
        let data = await promise;
        if (data.success) {
            console.debug("Got executed", data, "promise", promise);
        } else {
            console.warn("Execute failed:", data, "promise", promise);
        }

    })();
}

export function setServer(s: ServerAPI) {
    server = s;
}

export function setMedalsEnabled(enableMedals: boolean): Promise<any> {
    return server!.callPluginMethod("setMedalsEnabled", { "enableMedals": enableMedals});
}

// Python functions
export function getMedalsEnabled(): Promise<any> {
    return server!.callPluginMethod("areMedalsEnabled", {});
}