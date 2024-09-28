import os
from dataclasses import dataclass

from AppKit import NSWorkspace
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID

@dataclass(frozen=True)
class Rectangle:
    x: int
    y: int
    width: int
    height: int

class MacOSManager():

    def list_open_applications(self):
        workspace = NSWorkspace.sharedWorkspace()
        # Get the list of running applications
        running_apps = workspace.runningApplications()

        # Extract and return the names of the open applications
        open_app_names = [app.localizedName() for app in running_apps]
        return open_app_names

    def list_installed_apps(self):
        app_dirs = ["/Applications", "/System/Applications", os.path.expanduser("~/Applications")]
        installed_apps = []
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                apps = [f for f in os.listdir(app_dir) if f.endswith(".app")]
                installed_apps.extend(apps)

        return installed_apps

    def get_app_window_rectangle(self, app_name: str) -> Rectangle:
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
        print(f"Searching {app_name} for bounds extraction..")
        for window in window_list:
            # Get the application name and check if it is iTerm
            if app_name.lower() in window.get('kCGWindowOwnerName', '').lower():
                if window.get("kCGWindowName"): # this can introduce some bugs!!
                    print(f"Found them. Here {window.get('kCGWindowOwnerName', '')}")
                    # Get the bounds of the iTerm window
                    bounds = window['kCGWindowBounds']
                    x = int(bounds['X'])
                    y = int(bounds['Y'])
                    width = int(bounds['Width'])
                    height = int(bounds['Height'])
                    return Rectangle(x, y, width, height)
        return None
