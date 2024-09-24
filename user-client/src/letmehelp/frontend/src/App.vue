<script lang="ts" setup>
import Query from './components/Query.vue'</script>

<template>
  <div class="container">
    <img id="logo" alt="Wails logo" src="./assets/images/logo-universal.png"/>
    <Query/>
  </div>
</template>

<style>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
#logo {
  display: block;
  width: 200px;
}
</style>
