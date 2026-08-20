const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("cawl", {
  status: () => ipcRenderer.invoke("cawl:status"),
  restartServer: () => ipcRenderer.invoke("cawl:restart-server"),
});
