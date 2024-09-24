<script lang="ts" setup>
import {reactive, ref} from 'vue'
import {Query, Screenshot, GetCursorLocation, TypeWithKeyboard, MoveCursor} from '../../wailsjs/go/main/App'
import {WindowGetPosition, WindowHide, WindowSetPosition, WindowShow} from "../../wailsjs/runtime";

const queryInput = ref<HTMLInputElement | null>(null)

// TODO: Implement a WebSocket connection to an API for bi-directional communication.
// TODO: Implement all possible commands (e.g. click on a specific location, emit keyboard events to type, take a screenshot, etc.)

const data = reactive({
  query: "",
  agentMessage: "How may I help you?",
  screenshotBase64: ""
})

function query() {
  Query(data.query).then(agentMessage => {
    data.agentMessage = agentMessage
  })
}

function screenshot() {
  Screenshot().then(base64Image => {
    data.screenshotBase64 = base64Image
  })
}

function randomIntFromInterval(min: number, max: number) { // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

async function moveCursor() {
  // TODO: Take input
  let pos = await WindowGetPosition()
  await MoveCursor(pos.x + randomIntFromInterval(50, 400), pos.y + randomIntFromInterval(50, 400))
}

function typeWithKeyboard() {
  // TODO: Take input
  if (queryInput.value) {
    queryInput.value.focus()
  }
  TypeWithKeyboard("LetMeHelp is awesome!")
}

function getCursorLocation() {
  GetCursorLocation().then(coordinates => {
    data.agentMessage = coordinates
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
    <div id="agent-message" class="agent-message">{{ data.agentMessage }}</div>
    <div id="input" class="input-box">
      <input ref="queryInput" id="query" v-model="data.query" autocomplete="off" class="input" type="text" v-on:keyup.enter="query" />
      <button class="btn" @click="query">Send</button>
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

<style scoped>
.agent-message {
  height: 20px;
  line-height: 20px;
  margin: 1rem auto;
}

.input-box .btn {
  width: 60px;
  height: 32px;
  margin: 0 0 0 10px;
  padding: 0 8px;
  cursor: pointer;
}

.input-box .input {
  height: 30px;
  padding: 0 10px;
}


.debug {
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
