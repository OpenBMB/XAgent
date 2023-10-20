<template>
  <section class="container-box flex-column">
    <Setting @settingChange="settingChange" />
    <FileUpload/>
    <div class="input-border flex-column">
      <div class="input-box">
        <TalkInput :message="input" @send-message="sendMessage"/>
      </div>
      <div class="warning flex-row">
        <span> Disclaimer: The content is probabilistically generated  by the model, 
          and does NOT represent the developer's viewpoint</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">

import Setting from "./components/Setting.vue";
import FileUpload from "./components/FileUpload.vue";
import { ElMessage } from "element-plus";
import generateRandomId from "/@/utils/uuid";

const chatMsgInfoStore = useHistoryTalkStore()
useAsset('/path')
const input = ref('')
const router = useRouter()
const historyTalkStore = useHistoryTalkStore()

const agent = ref('');
const mode = ref('')

const settingChange = (val: any) => {
  agent.value = val.agent
  mode.value = val.mode
  chatMsgInfoStore.setSetting('config', val)
}

const sendMessage = (val: string) => {
  const uuid = generateRandomId();
  if(agent.value === "" || mode.value === "") {
    ElMessage({
      message: 'Please select agent and mode first',
      type: 'warning'
    });
    nextTick(() => {
      input.value = val;
    })
  }  else if ( val === '') {
    ElMessage({
      message: 'Please input message',
      type: 'warning'
    });
  } else {
    historyTalkStore.setCurrentInput(val)
    console.log("这是一个新建的对话")
    console.log(uuid)
    
    router.push({
      name: 'NewTalk',
      params: {
        mode: "new",
        id: uuid,
      }});
  }
}
</script>

<style scoped lang="scss">
.container-box {
  position: relative;
  background-color: rgb(236, 237, 245);
  padding: 34px calc(50% - 26vw) 60px;
  width: 100%;
  gap: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;

  .news,
  .ability,
  .feature {
    gap: 24px;
    width: calc(100% / 3);
  }
}
.input-border{
  z-index: 5;
  position: absolute;
  left: 0px;
  bottom: 0px;
  width: 100%;
  align-items: center;
  padding-top: 16px;
  background: rgb(240,241,250);
  box-shadow: inset 0 1px 3px 0 #FFFFFF;
  .input-box {
    width: 52vw;
  }

  .warning {
    width: 64vw;
    justify-content: center;
    font-family: PingFangSC-Regular;
    font-size: 12px;
    color: #dddddd;
    font-weight: 400;
    margin-top: 32px;
    margin-bottom: 20px;
    gap: 24px;
    text-align: center;
    span {
      color: #ddd;
      text-decoration: none;
    }
    span:active {
      color: #ddd;
    }
  }
}

// @media screen and (max-width: 1440px) {
  
// }
</style>
