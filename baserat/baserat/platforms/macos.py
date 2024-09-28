from AppKit import NSWorkspace



class MacOSManager():

    def list_open_applications(self):
        workspace = NSWorkspace.sharedWorkspace()
        # Get the list of running applications
        running_apps = workspace.runningApplications()

        # Extract and return the names of the open applications
        open_app_names = [app.localizedName() for app in running_apps]
        return open_app_names