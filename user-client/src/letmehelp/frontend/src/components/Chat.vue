<script lang="ts" setup>
import {nextTick, reactive, ref} from 'vue'
import {Query, Screenshot, GetCursorLocation, TypeWithKeyboard, MoveCursor} from '../../wailsjs/go/main/App'
import {WindowGetPosition, WindowHide, WindowSetPosition, WindowShow} from "../../wailsjs/runtime"

interface Message {
  from: string
  content: string
}

interface Data {
  query: string,
  screenshotBase64: string,
  messages: Message[]
}

const userInput = ref<HTMLTextAreaElement | null>(null)
const messagesContainer = ref<HTMLDivElement | null>(null)

const data: Data = reactive({
  query: "",
  screenshotBase64: "",
  messages: []
})

const adjustTextarea = () => {
  if (userInput.value) {
    userInput.value!.scrollTop = userInput.value!.scrollHeight
  }
}

async function addMessage(from: string, content: string) {
  let message: Message = {
    from: from,
    content: content
  }
  data.messages.push(message)
  await nextTick();
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

function query() {
  data.query = data.query.trim()
  if (!data.query) {
    return
  }
  addUserMessage(data.query)
  Query(data.query).then(serverMessage => {
    // ABSOLUTELY IMPORTANT TODO: WHEN THE USER HAS JUST SENT A MESSAGE,
    // WE EITHER HAVE TO DISABLE THE INPUT BOX UNTIL THE SERVER HAS RESPONDED (EASY),
    // OR LET THE USER KEEP SENDING MESSAGES, BUT THE SERVER DECIDES WHEN TO RESPOND
    // AND TO WHICH MESSAGE (DIFFICULT).
    // TODO: How to check for action inside the message and act accordingly?
    // Those items probably also need some message to show to the user, but also an action to be executed.
    addServerMessage(serverMessage)
    data.query = ""
  })
}

async function screenshot() {
  let pos = await WindowGetPosition()
  WindowHide()
  setTimeout(function(){
    Screenshot().then(base64Image => {
      data.screenshotBase64 = base64Image
      WindowShow()
      WindowSetPosition(pos.x, pos.y)
    })
  }, 500)
}

function randomIntFromInterval(min: number, max: number) { // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min)
}

async function moveCursor() {
  // TODO: Take input
  let pos = await WindowGetPosition()
  await MoveCursor(pos.x + randomIntFromInterval(50, 400), pos.y + randomIntFromInterval(50, 400))
}

function typeWithKeyboard() {
  // TODO: Take input
  if (userInput.value) {
    userInput.value.focus()
  }
  TypeWithKeyboard("LetMeHelp is awesome!")
}

function getCursorLocation() {
  GetCursorLocation().then(coordinates => {
    addMessage("system", coordinates)
  })
}

async function showAndHide() {
  // TODO: Take input
  let pos = await WindowGetPosition()
  WindowHide()
  setTimeout(function() {
    WindowShow()
    WindowSetPosition(pos.x, pos.y)
  }, 1000)
}
</script>

<template>
  <main>
    <div ref="messagesContainer" class="messages">
      <div class="message" :class="{'user-message': message.from == 'user', 'server-message': message.from == 'server'}" v-for="message in data.messages">
        <span class="icon" v-if="message.from == 'user'"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg></span>
        <span class="icon" v-if="message.from == 'server'"><img src="../assets/images/letmehelp-icon.png"/></span>
        {{ message.content }}
      </div>
    </div>
    <div class="input-box">
      <div class="input-wrapper">
        <textarea placeholder="Send message" @input="adjustTextarea" ref="userInput" id="query" v-model="data.query" autocomplete="off" type="text" @keydown.enter.exact.prevent="query">
        </textarea>
        <button class="btn" @click="query">Send</button>
      </div>
    </div>
    <div class="debug">
      <div class="buttons">
        <button class="btn" @click="screenshot">Screenshot</button>
        <button class="btn" @click="moveCursor">Move Cursor</button>
        <button class="btn" @click="typeWithKeyboard">Type with Keyboard</button>
        <button class="btn" @click="getCursorLocation">Get Cursor Location</button>
        <button class="btn" @click="showAndHide">Show and Hide Window</button>
      </div>
      <img v-if="data.screenshotBase64" alt="" v-bind:src="'data:image/jpeg;base64,'+data.screenshotBase64" onerror="this.style.display='none'"/>
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

.messages {
  background: #fbfbfb;
  height: 295px;
  overflow-y: scroll;
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

/* ----- */
/* Debug */
/* ----- */

.debug {
  /* Remove display: none; to enable debug mode. */
  display: none;
  margin-top: 15px;
  width: 100%;
}

.debug .buttons {
  margin: auto auto 15px;
  width: 100%;
}

.debug .buttons button {
  margin-right: 5px;
  margin-bottom: 5px;
}

.debug img {
  display: block;
  width: auto;
  height: 150px;
  margin: auto;
}
</style>
