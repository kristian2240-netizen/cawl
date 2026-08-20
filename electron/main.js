const { app, BrowserWindow, ipcMain, dialog, shell } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const http = require("http");

const CAWL_PORT = 8123;
const CAWL_URL = `http://127.0.0.1:${CAWL_PORT}`;
const PROJECT_ROOT = path.resolve(__dirname, "..");

let mainWindow = null;
let serverProcess = null;
let serverReady = false;

function findPython() {
  const candidates = [
    path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe"),
    "python",
    "python3",
  ];
  return candidates[0];
}

function startServer() {
  if (serverProcess) return;

  const python = findPython();
  const args = ["-m", "test_project.main"];

  console.log(`[CAWL] Starting server: ${python} ${args.join(" ")}`);
  serverProcess = spawn(python, args, {
    cwd: PROJECT_ROOT,
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, CAWL_HOST: "127.0.0.1", CAWL_PORT: String(CAWL_PORT) },
  });

  serverProcess.stdout.on("data", (d) => {
    const msg = d.toString();
    console.log(`[CAWL server] ${msg.trim()}`);
    if (msg.includes("Uvicorn running") || msg.includes("Application startup complete")) {
      serverReady = true;
      loadCAWL();
    }
  });

  serverProcess.stderr.on("data", (d) => {
    console.error(`[CAWL server] ${d.toString().trim()}`);
  });

  serverProcess.on("error", (err) => {
    console.error("[CAWL] Failed to start server:", err.message);
    dialog.showErrorBox("C.A.W.L. Server Error", `Failed to start the server:\n${err.message}`);
  });

  serverProcess.on("close", (code) => {
    console.log(`[CAWL] Server exited with code ${code}`);
    serverProcess = null;
    serverReady = false;
  });
}

function waitForServer(retries = 40, delay = 500) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const check = () => {
      http.get(`${CAWL_URL}/self`, (res) => {
        let body = "";
        res.on("data", (d) => (body += d));
        res.on("end", () => {
          try {
            JSON.parse(body);
            serverReady = true;
            resolve();
          } catch {
            retry();
          }
        });
      }).on("error", retry);
    };
    const retry = () => {
      attempts++;
      if (attempts >= retries) {
        reject(new Error("Server did not start in time"));
      } else {
        setTimeout(check, delay);
      }
    };
    check();
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    title: "C.A.W.L. — Archmagos Dominus",
    icon: path.join(PROJECT_ROOT, "src", "test_project", "static", "cawl_avatar.png"),
    backgroundColor: "#0a0d12",
    titleBarStyle: "hiddenInset",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
      spellcheck: false,
    },
    show: false,
  });

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.loadFile(path.join(__dirname, "loading.html"));
  startServer();
  waitForServer()
    .then(() => loadCAWL())
    .catch((err) => {
      console.error("[CAWL]", err.message);
      if (mainWindow) {
        mainWindow.webContents.loadFile(path.join(__dirname, "error.html"));
      }
    });
}

function loadCAWL() {
  if (mainWindow && serverReady) {
    mainWindow.loadURL(CAWL_URL);
  }
}

ipcMain.handle("cawl:status", async () => {
  return new Promise((resolve) => {
    http.get(`${CAWL_URL}/self`, (res) => {
      let body = "";
      res.on("data", (d) => (body += d));
      res.on("end", () => {
        try {
          resolve({ ok: true, data: JSON.parse(body) });
        } catch {
          resolve({ ok: false });
        }
      });
    }).on("error", () => resolve({ ok: false }));
  });
});

ipcMain.handle("cawl:restart-server", async () => {
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
    serverReady = false;
  }
  startServer();
  try {
    await waitForServer();
    loadCAWL();
    return { ok: true };
  } catch {
    return { ok: false };
  }
});

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (serverProcess) {
    serverProcess.kill();
  }
  app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
