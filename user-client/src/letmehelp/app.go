package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os/exec"
	"strings"

	"github.com/go-vgo/robotgo"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// getCoordinateOffsets solves an issue where coordinates of windows in different platforms are a bit off.
func (a *App) getCoordinateOffsets() (appWidthOffset int, appHeightOffset int) {
	switch runtime.Environment(a.ctx).Platform {
	case "windows":
		// screenWidth and screenHeight don't seem be accurate on Windows :/
		// We need to figure out some offset to make it go to the edge.
		appHeightOffset = 105
		appWidthOffset = 290
		break
	case "linux":
		// All good here.
		break
	case "darwin":
		// Same issue, but the window needs to be moved up a bit.
		appHeightOffset = -50
		break
	}
	return appWidthOffset, appHeightOffset
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	// Move the window to the bottom right corner
	screens, err := runtime.ScreenGetAll(ctx)
	if err != nil {
		return
	}
	var screenWidth, screenHeight int
	for _, screen := range screens {
		if screen.IsCurrent {
			screenWidth = screen.Size.Width
			screenHeight = screen.Size.Height
			break
		}
	}
	appWidthOffset, appHeightOffset := a.getCoordinateOffsets()
	runtime.WindowSetPosition(ctx, screenWidth-appWidth+appWidthOffset, screenHeight-appHeight+appHeightOffset)
}

// Screenshot takes a screenshot and returns the base64 encoded image
func (a *App) Screenshot() (string, error) {
	// TODO: How to find the active screen?
	// For now take a screenshot of the primary screen
	screenshot := robotgo.CaptureScreen()
	return string(robotgo.ToByteImg(robotgo.ToImage(screenshot))), nil
}

// Screenshot takes a screenshot of the application identified by the PID and returns the base64 encoded image
func (a *App) ScreenshotByPID(pid int) (string, error) {
	// 1. Bring the application to foreground
	err := a.BringApplicationToForegroundByPID(pid)
	if err != nil {
		return "", err
	}

	// 2. Get the bounding box of the application
	boundingBox, err := a.GetApplicationBoundingBoxByPID(pid)
	if err != nil {
		return "", err
	}

	// 3. Take a screenshot of the bounding box
	// TODO: For some reason the screenshot is a bit off when tested in Windows.
	screenshot := robotgo.CaptureScreen(boundingBox.Top, boundingBox.Left, boundingBox.Right, boundingBox.Bottom)
	return string(robotgo.ToByteImg(robotgo.ToImage(screenshot))), nil
}

// GetCursorLocation returns the (x,y) coordinates of the current cursor location
func (a *App) GetCursorLocation() string {
	x, y := robotgo.Location()
	return fmt.Sprintf("(%d, %d)", x, y)
}

// TypeWithKeyboard types the input string
func (a *App) TypeWithKeyboard(input string) {
	robotgo.TypeStr(input)
}

// CursorClick moves the cursor to the specified x and y coordinates and clicks
func (a *App) CursorClick(x int, y int) {
	robotgo.Move(x, y)
	robotgo.Click()
}

// GetInstalledApplications retrieves the list of installed applications.
// This is a platform-specific command.
func (a *App) GetInstalledApplications() ([]string, error) {
	switch runtime.Environment(a.ctx).Platform {
	case "windows":
		// Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | findstr "DisplayName" | ConvertTo-Json
		// Then convert to JSON
		return nil, fmt.Errorf("Not implemented yet for Windows!")
	case "linux":
		return nil, fmt.Errorf("Not implemented yet for Linux!")
	case "darwin":
		out, err := exec.Command("ls", "-1a", "/Applications").Output()
		if err != nil {
			return nil, err
		}
		outStr := string(out)
		return strings.Split(outStr, "\n"), nil
	}
	return nil, fmt.Errorf("Failed to detect client platform.")
}

type KeyCombo struct {
	Key       string   // e.g. "f4"
	Modifiers []string // e.g. ["alt"]
}

// PressKeyCombo presses the combination of specified keys.
// Possible keys: https://github.com/go-vgo/robotgo/blob/master/docs/keys.md
// The main key always comes first, followed by modifiers.
func (a *App) PressKeyCombo(input KeyCombo) {
	robotgo.KeySleep = 100
	robotgo.KeyTap(input.Key, input.Modifiers)
}

type RunningApplication struct {
	ProcessID   int
	ProcessName string
	WindowTitle string
}

type WindowsProcessInfo struct {
	Id              int    `json:"Id"`
	ProcessName     string `json:"ProcessName"`
	MainWindowTitle string `json:"MainWindowTitle"`
}

// GetRunningApplications retrieves the list of running applications.
func (a *App) GetRunningApplications() ([]RunningApplication, error) {
	switch runtime.Environment(a.ctx).Platform {
	case "windows":
		out, err := exec.Command("powershell", "/C", `Get-Process | Select MainWindowTitle,ProcessName,Id | where{$_.MainWindowTitle -ne ""} | ConvertTo-Json`).Output()
		if err != nil {
			return nil, err
		}
		var windowsProcesses []WindowsProcessInfo
		json.Unmarshal(out, &windowsProcesses)
		runningApplications := make([]RunningApplication, len(windowsProcesses))
		for i, p := range windowsProcesses {
			runningApplications[i] = RunningApplication{
				ProcessID:   p.Id,
				ProcessName: p.ProcessName,
				WindowTitle: p.MainWindowTitle,
			}
		}
		return runningApplications, nil
	case "linux":
		return nil, fmt.Errorf("Not implemented yet for Linux!")
	case "darwin":
		return nil, fmt.Errorf("Not implemented yet for Mac!")
	}
	return nil, fmt.Errorf("Failed to detect client platform.")
}

type ApplicationBoundingBox struct {
	Top    int `json:"top"`
	Left   int `json:"left"`
	Bottom int `json:"bottom"`
	Right  int `json:"right"`
	PID    int
}

// Get bounding box of application by PID
func (a *App) GetApplicationBoundingBoxByPID(pid int) (ApplicationBoundingBox, error) {
	switch runtime.Environment(a.ctx).Platform {
	case "windows":
		out, err := exec.Command("powershell", "/C", fmt.Sprintf("Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class Win32 {[DllImport(\"user32.dll\")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);public struct RECT {public int Left;public int Top;public int Right;public int Bottom;}}' ; $rect = New-Object Win32+RECT; [Win32]::GetWindowRect((Get-Process -Id %d).MainWindowHandle, [ref]$rect) | Out-Null; ConvertTo-Json @{Left=$rect.Left; Top=$rect.Top; Right=$rect.Right; Bottom=$rect.Bottom}", pid)).Output()
		if err != nil {
			return ApplicationBoundingBox{}, err
		}
		var boundingBox ApplicationBoundingBox
		boundingBox.PID = pid
		json.Unmarshal(out, &boundingBox)
		return boundingBox, nil
	case "linux":
		// xdotool search --pid $PID
		return ApplicationBoundingBox{}, fmt.Errorf("Not implemented yet for Linux!")
	case "darwin":
		// osascript -e "tell application \"System Events\" to tell (first process whose unix id is $PID) to get properties of window 1" | grep -E 'position:|size:'
		return ApplicationBoundingBox{}, fmt.Errorf("Not implemented yet for Mac!")
	}
	return ApplicationBoundingBox{}, fmt.Errorf("Failed to detect client platform.")
}

// BringApplicationToForeground brings the application window identified by the PID to the foreground.
func (a *App) BringApplicationToForegroundByPID(pid int) error {
	switch runtime.Environment(a.ctx).Platform {
	case "windows":
		_, err := exec.Command("powershell", "/C", fmt.Sprintf("(New-Object -ComObject WScript.Shell).AppActivate((Get-Process -Id %d).MainWindowTitle)", pid)).Output()
		if err != nil {
			return err
		}
		return nil
	case "linux":
		return fmt.Errorf("Not implemented yet for Linux!")
	case "darwin":
		return fmt.Errorf("Not implemented yet for Mac!")
	}
	return fmt.Errorf("Failed to detect client platform.")
}
