import src.uicomponents as uicomponents
import src.variables as variables
import src.console as console
import src.ui as ui

import subprocess
import shutil
import os


def CloseSetupCallback():
    for widget in ui.tab_MainMenu.winfo_children():
        widget.destroy()
    ui.InitializeMainMenu()


def OpenMainSetupCallback():
    for widget in ui.tab_MainMenu.winfo_children():
        widget.destroy()
    uicomponents.MakeLabel(ui.tab_MainMenu, "SDK and API installation", row=1, column=0, sticky="n", font=("Segoe UI", 15))
    any_error = False
    if variables.OS == "nt":
        try:
            import winreg
            uicomponents.MakeLabel(ui.tab_MainMenu, "> Searching for Steam...", row=2, column=0, sticky="n")
            STEAM_PATH = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam"), "SteamPath")[0]
            if os.path.exists(STEAM_PATH):
                uicomponents.MakeLabel(ui.tab_MainMenu, f"> Found Steam at {STEAM_PATH}", row=3, column=0, sticky="n")
                ETS2_STEAM_PATH = STEAM_PATH + r"/steamapps/common/Euro Truck Simulator 2"
                ATS_STEAM_PATH = STEAM_PATH + r"/steamapps/common/American Truck Simulator"
                if os.path.exists(ETS2_STEAM_PATH) or os.path.exists(ATS_STEAM_PATH):
                    if os.path.exists(ETS2_STEAM_PATH):
                        uicomponents.MakeLabel(ui.tab_MainMenu, f"> ETS2 found at {ETS2_STEAM_PATH}", row=4, column=0, sticky="n")
                        any_ets2_error = False
                        try:
                            if not os.path.exists(os.path.join(ETS2_STEAM_PATH, "bin", "win_x64", "plugins")):
                                os.makedirs(os.path.join(ETS2_STEAM_PATH, "bin", "win_x64", "plugins"))
                        except:
                            any_error = True
                            any_ets2_error = True
                        try:
                            if not os.path.exists(os.path.join(ETS2_STEAM_PATH, "bin", "win_x64", "plugins", "input_semantical.dll")):
                                shutil.copy2(os.path.join(variables.PATH, "app", "assets", "input_semantical.dll"), os.path.join(ETS2_STEAM_PATH, "bin", "win_x64", "plugins", "input_semantical.dll"))
                        except:
                            any_error = True
                            any_ets2_error = True
                        try:
                            if not os.path.exists(os.path.join(ETS2_STEAM_PATH, "bin", "win_x64", "plugins", "scs-telemetry.dll")):
                                shutil.copy2(os.path.join(variables.PATH, "app", "assets", "scs-telemetry.dll"), os.path.join(ETS2_STEAM_PATH, "bin", "win_x64", "plugins", "scs-telemetry.dll"))
                        except:
                            any_error = True
                            any_ets2_error = True
                        if any_ets2_error == True:
                            uicomponents.MakeLabel(ui.tab_MainMenu, f"ERROR: Failed to copy the dll files to the ETS2 directory", row=5, column=0, sticky="n")
                    if os.path.exists(ATS_STEAM_PATH):
                        uicomponents.MakeLabel(ui.tab_MainMenu, f"> ATS found at {ATS_STEAM_PATH}", row=6, column=0, sticky="n")
                        any_ats_error = False
                        try:
                            if not os.path.exists(os.path.join(ATS_STEAM_PATH, "bin", "win_x64", "plugins")):
                                os.makedirs(os.path.join(ATS_STEAM_PATH, "bin", "win_x64", "plugins"))
                        except:
                            any_error = True
                            any_ats_error = True
                        try:
                            if not os.path.exists(os.path.join(ATS_STEAM_PATH, "bin", "win_x64", "plugins", "input_semantical.dll")):
                                shutil.copy2(os.path.join(variables.PATH, "app", "assets", "input_semantical.dll"), os.path.join(ATS_STEAM_PATH, "bin", "win_x64", "plugins", "input_semantical.dll"))
                        except:
                            any_error = True
                            any_ats_error = True
                        try:
                            if not os.path.exists(os.path.join(ATS_STEAM_PATH, "bin", "win_x64", "plugins", "scs-telemetry.dll")):
                                shutil.copy2(os.path.join(variables.PATH, "app", "assets", "scs-telemetry.dll"), os.path.join(ATS_STEAM_PATH, "bin", "win_x64", "plugins", "scs-telemetry.dll"))
                        except:
                            any_error = True
                            any_ats_error = True
                        if any_ats_error == True:
                            uicomponents.MakeLabel(ui.tab_MainMenu, f"ERROR: Failed to copy the dll files to the ATS directory", row=7, column=0, sticky="n")
                else:
                    any_error = True
                    uicomponents.MakeLabel(ui.tab_MainMenu, "> ETS2 or ATS could not be found in the Steam directory...", row=4, column=0, sticky="n")
        except:
            any_error = True
        if any_error == True:
            uicomponents.MakeLabel(ui.tab_MainMenu, f"\nThe main setup could not be completed. Check the console for the manual setup instructions.", row=8, column=0, sticky="s")
            print(f"\nPlease do the setup manually by copying these files:\n{variables.PATH}app/assets/input_semantical.dll\n{variables.PATH}app/assets/scs-telemetry.dll\nto these folders (depending on your installed game):\nYOUR-STEAM-PATH/steamapps/common/Euro Truck Simulator 2/bin/win_x64/plugins\nYOUR-STEAM-PATH/steamapps/common/American Truck Simulator/bin/win_x64/plugins\nCreate the plugins folder if it does not exist.\n")
            console.RestoreConsole()
        else:
            uicomponents.MakeLabel(ui.tab_MainMenu, "The main setup was completed successfully!", row=8, column=0, sticky="s")
        uicomponents.MakeButton(ui.tab_MainMenu, "Exit", lambda: CloseSetupCallback(), row=9, column=0, sticky="s", pady=5, padx=5)
    else:
        uicomponents.MakeLabel(ui.tab_MainMenu, "The main setup is only available on Windows. Check the console for the manual setup instructions.", row=2, column=0, sticky="s")
        print(f"\nPlease do the setup manually by copying these files:\n{variables.PATH}app/assets/input_semantical.dll\n{variables.PATH}app/assets/scs-telemetry.dll\nto these folders (depending on your installed game):\nYOUR-STEAM-PATH/steamapps/common/Euro Truck Simulator 2/bin/win_x64/plugins\nYOUR-STEAM-PATH/steamapps/common/American Truck Simulator/bin/win_x64/plugins\nCreate the plugins folder if it does not exist.\n")
        console.RestoreConsole()
        uicomponents.MakeButton(ui.tab_MainMenu, "Exit", lambda: CloseSetupCallback(), row=3, column=0, sticky="s", pady=5, padx=5)

def OpenNavigationDetectionAISetupCallback():
    for widget in ui.tab_MainMenu.winfo_children():
        widget.destroy()
    uicomponents.MakeLabel(ui.tab_MainMenu, "Which setup method would you like to use?", row=1, column=0, sticky="n", font=("Segoe UI", 15))
    def AutomaticSetupCallback():
        for widget in ui.tab_MainMenu.winfo_children():
            widget.destroy()
        ui.InitializeMainMenu()
        subprocess.Popen(["python", os.path.join(variables.PATH, "app", "plugins", "NavigationDetectionAI", "automatic_setup.py")])
    uicomponents.MakeButton(ui.tab_MainMenu, "Automatic Setup", lambda: AutomaticSetupCallback(), row=2, column=0, sticky="nw", padx=20, pady=30, width=35)
    def ManualSetupCallback():
        for widget in ui.tab_MainMenu.winfo_children():
            widget.destroy()
        ui.InitializeMainMenu()
        subprocess.Popen(["python", os.path.join(variables.PATH, "app", "plugins", "NavigationDetectionAI", "manual_setup.py")])
    uicomponents.MakeButton(ui.tab_MainMenu, "Manual Setup", lambda: ManualSetupCallback(), row=2, column=0, sticky="ne", padx=20, pady=30, width=35)
    def ExitNavigationDetectionAISetupCallback():
        for widget in ui.tab_MainMenu.winfo_children():
            widget.destroy()
        ui.InitializeMainMenu()
    uicomponents.MakeButton(ui.tab_MainMenu, "Exit", lambda: ExitNavigationDetectionAISetupCallback(), row=3, column=0, sticky="n")