<script lang="ts" setup>
import Chat from './components/Chat.vue'</script>

<template>
  <div class="container">
    <div id="logo">
      <div class="logo-bg"></div>
      <img alt="LetMeHelp logo" src="./assets/images/logo-universal.png"/>
    </div>
    <Chat/>
  </div>
</template>

<style>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
}
#logo {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.logo-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 138px;
  z-index: -999;
  opacity: 0.15;
  background-color:#bef0ff;
background-image:
radial-gradient(circle at 100% 150%, #bef0ff 24%, white 24%, white 28%, #bef0ff 28%, #bef0ff 36%, white 36%, white 40%, transparent 40%, transparent),
radial-gradient(circle at 0    150%, #bef0ff 24%, white 24%, white 28%, #bef0ff 28%, #bef0ff 36%, white 36%, white 40%, transparent 40%, transparent),
radial-gradient(circle at 50%  100%, white 10%, #bef0ff 10%, #bef0ff 23%, white 23%, white 30%, #bef0ff 30%, #bef0ff 43%, white 43%, white 50%, #bef0ff 50%, #bef0ff 63%, white 63%, white 71%, transparent 71%, transparent),
radial-gradient(circle at 100% 50%, white 5%, #bef0ff 5%, #bef0ff 15%, white 15%, white 20%, #bef0ff 20%, #bef0ff 29%, white 29%, white 34%, #bef0ff 34%, #bef0ff 44%, white 44%, white 49%, transparent 49%, transparent),
radial-gradient(circle at 0    50%, white 5%, #bef0ff 5%, #bef0ff 15%, white 15%, white 20%, #bef0ff 20%, #bef0ff 29%, white 29%, white 34%, #bef0ff 34%, #bef0ff 44%, white 44%, white 49%, transparent 49%, transparent);
background-size: 100px 50px;
}

#logo img {
  width: 130px;
}
</style>
