package main

import (
	"context"
	"fmt"
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
	runtime.WindowSetPosition(ctx, screenWidth-appWidth, screenHeight-appHeight)
}

// Screenshot takes a screenshot and returns the base64 encoded image
func (a *App) Screenshot() string {
	// TODO: How to find the active screen?
	// For now take a screenshot of the primary screen
	screenshot := robotgo.CaptureScreen()
	return string(robotgo.ToByteImg(robotgo.ToImage(screenshot)))
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
