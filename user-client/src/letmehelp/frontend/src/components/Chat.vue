<script lang="ts" setup>
import {nextTick, reactive, ref} from 'vue'
import {Screenshot, GetCursorLocation, TypeWithKeyboard, CursorClick, GetInstalledApplications, PressKeyCombo, GetRunningApplications, GetApplicationBoundingBoxByPID, BringApplicationToForegroundByPID, ScreenshotByPID} from '../../wailsjs/go/main/App'
import {WindowGetPosition, WindowHide, WindowSetPosition, WindowShow} from "../../wailsjs/runtime"

interface DisplayMessage {
  from: string
  content: string
}

interface Data {
  query: string,
  screenshotBase64: string,
  messages: DisplayMessage[],
  serverAddress: string,
  serverStatus: string,
  settingsModalOpen: boolean,
  socket: WebSocket|null
}

interface Message {
  type: string,
  value: any,
}

const userInput = ref<HTMLTextAreaElement | null>(null)
const messagesContainer = ref<HTMLDivElement | null>(null)

const data: Data = reactive({
  query: "",
  screenshotBase64: "",
  messages: [],
  serverAddress: "127.0.0.1:8765", // TODO: Change back to localhost or our server address
  serverStatus: "Disconnected",
  settingsModalOpen: false,
  socket: null,
})

function clearMessages() {
  data.messages = []
}

function connect() {
  if (data.socket) {
    data.socket.close()
  }
  data.serverStatus = "Connecting"
  // TODO: Clean up
  let socket = new WebSocket(`ws://${data.serverAddress}`)
  socket.onerror = function (event) {
      console.log("Error: ", event)
  }
  socket.onopen = function (event) {
    console.log("Open: ", event)
    data.serverStatus = "Connected"
    clearMessages()
  }
  socket.onclose = function (event) {
    console.log("Close: ", event)
    if (!event.wasClean) {
      data.serverStatus = "Error (see console)"
      addServerMessage("Failed to connect to the server. Please see settings.")
    } else {
      data.serverStatus = "Disconnected"
      addServerMessage("Server disconnected.")
    }
  }
  socket.onmessage = async function (event) {
    console.log("Message: ", event)
    if (event.data) {
      try {
        const response: Message = JSON.parse(event.data)
        switch (response.type) {
          case "error":
            // An error message from the server
            // TODO: Make this yellow.
            addServerMessage(`Oops! ${response.value}`)
            break
          case "text":
            // A textual message from the server
            addServerMessage(response.value)
            break
          case "get-screenshot":
            let screenshotData = await screenshot()
            sendSocketMessage("screenshot", screenshotData)
            break
            case "get-screenshot-by-pid":
            let screenshotByPIDData = await screenshotByPID(response.value)
            sendSocketMessage("screenshot-by-pid", screenshotByPIDData)
            break
          // TODO: Do we want to hide the window, perform the action, and show the window for all actions?
          case "get-cursor-location":
            let cursorLocation = await GetCursorLocation()
            sendSocketMessage("cursor-location", cursorLocation)
            break
          case "click-at":
            // TODO: Make this an array as input?
            let coordinates = response.value.split(",")
            if (coordinates.length !== 2) {
              addServerMessage("Oops! The server returned invalid coordinates to click at.")
              return
            }
            await CursorClick(parseInt(coordinates[0], 10), parseInt(coordinates[1], 10))
            break
          case "type-with-keyboard":
            await TypeWithKeyboard(response.value)
            break
          case "press-key-combo":
            await PressKeyCombo(response.value)
            break
          case "get-installed-applications":
            let installedApplications = await GetInstalledApplications()
            sendSocketMessage("installed-applications", installedApplications)
            break
          case "get-running-applications":
            let runningApplications = await GetRunningApplications()
            sendSocketMessage("running-applications", runningApplications)
            break
          case "get-application-bounding-box-by-pid":
            let applicationBoundingBox = await GetApplicationBoundingBoxByPID(response.value)
            sendSocketMessage("application-bounding-box", applicationBoundingBox)
            break
          case "bring-application-to-foreground-by-pid":
            await BringApplicationToForegroundByPID(response.value)
            break
          // TODO: Implement other message types
          /*case "your-action-name":
            // Do the action!
            break;*/
          default:
            addServerMessage(`Oops! The client doesn't support the message type (${response.type}).`)
            break
        }
      } catch(error) {
        addServerMessage("An error occurred while processing a server message. See console.")
        console.log("Error:", error)
      }
    }
  }
  data.socket = socket
}

connect()

function adjustTextarea() {
  if (userInput.value) {
    userInput.value!.scrollTop = userInput.value!.scrollHeight
  }
}

async function addMessage(from: string, content: string) {
  let message: DisplayMessage = {
    from: from,
    content: content
  }
  data.messages.push(message)
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value!.scrollTop = messagesContainer.value!.scrollHeight
  }
}

function addUserMessage(content: string) {
  addMessage("user", content)
}

function addServerMessage(content: string) {
  addMessage("server", content)
}

function sendSocketMessage(type: string, value: any) {
  if (data.socket && data.socket.readyState == 1) {
    // TODO: Right now, we're doing this asynchronously, meaning we don't block user input
    // until the server responds. The server should have a queue on its own end to respond to messages.
    // TODO: How to cancel the current operation (similar to stop generating in ChatGPT)?
    let msg: Message = {
      type: type,
      value: value,
    }
    let msgJSON: string = JSON.stringify(msg)
    data.socket.send(msgJSON)
  } else {
    addServerMessage("Server connection error. Please check settings.")
  }
}

function query() {
  data.query = data.query.trim()
  if (!data.query) {
    return
  }
  addUserMessage(data.query)
  sendSocketMessage("text", data.query)
  data.query = ""
}

async function screenshot() {
  let pos = await WindowGetPosition()
  WindowHide()
  // Wait for the screen to hide
  await new Promise(f => setTimeout(f, 500))
  let screenshotBase64Data = await Screenshot()
  // Restore the window
  WindowShow()
  WindowSetPosition(pos.x, pos.y)
  return screenshotBase64Data
}

async function screenshotByPID(pid: number) {
  let pos = await WindowGetPosition()
  WindowHide()
  // Wait for the screen to hide
  await new Promise(f => setTimeout(f, 500))
  let screenshotBase64Data = await ScreenshotByPID(pid)
  // Restore the window
  WindowShow()
  WindowSetPosition(pos.x, pos.y)
  return screenshotBase64Data
}
</script>

<template>
  <main>
    <div class="settings-modal" :style="{ display: data.settingsModalOpen ? 'flex' : 'none' }">
      <div class="input-group">
        <span>Server address:</span>
        <div class="contents">
          <input type="text" v-model="data.serverAddress" @keydown.enter.exact.prevent="connect"/>
          <button class="btn" @click="connect">Connect</button>
        </div>
      </div>
      <div class="input-group">
        <span>Status:</span>
        <div class="contents" :class="{'text-green': data.serverStatus == 'Connected', 'text-red': data.serverStatus.includes('Error')}">
          {{ data.serverStatus }}
        </div>
      </div>
    </div>
    <div class="top-icons">
      <button class="btn" @click="data.settingsModalOpen = !data.settingsModalOpen">
        <svg v-if="!data.settingsModalOpen" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
        <svg v-if="data.settingsModalOpen" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6"><path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" /></svg>
      </button>
    </div>
    <div ref="messagesContainer" class="messages">
      <div class="message" :class="{'user-message': message.from == 'user', 'server-message': message.from == 'server'}" v-for="message in data.messages">
        <span class="icon" v-if="message.from == 'user'"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg></span>
        <span class="icon" v-if="message.from == 'server'"><img src="../assets/images/letmehelp-icon.png"/></span>
        {{ message.content }}
      </div>
    </div>
    <div class="input-box" :style="{ display: data.settingsModalOpen ? 'none' : 'flex' }">
      <div class="input-wrapper">
        <textarea spellcheck="false" placeholder="Send message" @input="adjustTextarea" ref="userInput" id="query" v-model="data.query" autocomplete="off" type="text" @keydown.enter.exact.prevent="query">
        </textarea>
        <button class="btn" @click="query">Send</button>
      </div>
    </div>
  </main>
</template>

<style>
body {
  overflow: hidden;
}
</style>

<style scoped>
main {
  border-top: 2px solid #f3f3f3;
  width: 100%;
  height: 100%;
  display: block;
}

.text-green {
  color: green;
}

.text-red {
  color: red;
}

.settings-modal {
  position: absolute;
  background: #fbfbfb;
  height: 355px;
  width: 100%;
  display: flex;
  flex-direction: column;
  text-align: left;
  padding-top: 10px;
}

.input-group {
  display: flex;
  padding: 10px 20px;
  align-items: center;
  line-height: 1em;
  font-size: 14px;
}

.input-group span {
  flex-basis: 25%;
  font-weight: 600;
}

.input-group .contents {
  display: flex;
  flex-basis: 75%;
}

.input-group input {
  width: 70%;
  padding: 10px;
  font-size: 13px;
}

.input-group .btn {
  margin-left: 10px;
  width: 30%;
}

.messages {
  background: #fbfbfb;
  height: 256px;
  overflow-y: scroll;
  font-size: 13px;
}

.message {
  padding: 15px;
  text-align: left;
  display: flex;
  align-items: center;
}

.icon {
  margin-right: 10px;
  display: flex;
  align-self: baseline;
}

.icon svg, .icon img {
  width: 30px;
}

.server-message{
  background: #f5fcff;
  border: 1px solid #d7f4ff;
  border-left: none;
  border-right: none;
}

.user-message{
  background: #ffffff;
}

.input-box {
  border-top: 2px solid #f3f3f3;
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 70px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fff;
}

.input-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 0 6px;
}

.input-box .btn {
  width: 20%;
  height: 59px;
  margin: 0 0 0 8px;
  padding: 0 8px;
  cursor: pointer;
  outline: none;
  border-radius: 15px;
  border: 1px solid #8cd9ff;
  color: #0088c1;
  background: #f5fcff;
  flex-basis: 20%;
}

.input-box textarea {
  height: 25px;
  margin: 0;
  padding: 15px;
  resize: none;
  border-radius: 15px;
  border: 1px solid #dcdcdc;
  white-space: normal;
  flex-basis: 80%;
}

.top-icons {
  position: absolute;
  top: 20px;
  right: 20px;
}

.top-icons svg {
  width: 100%;
  height: 100%;
}

.top-icons .btn {
  display: flex;
  height: 40px;
  width: 40px;
  margin: 0 0 0 8px;
  padding: 0 8px;
  cursor: pointer;
  outline: none;
  border-radius: 15px;
  border: 1px solid #8cd9ff;
  color: #0088c1;
  background: #f5fcff;
}
</style>
