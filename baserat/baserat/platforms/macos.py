import os
from AppKit import NSWorkspace


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
