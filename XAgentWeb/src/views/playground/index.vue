<template>
  <div class="config-cards">
      <Setting @settingChange="settingChange" />
      <FileUpload/>      
  </div>
  <div class="input-border flex-column">
    <div class="input-box">
      <TalkInput :message="input" @send-message="sendMessage"/>
    </div>
    <div class="warning flex-row">
      <span> Disclaimer: The content is probabilistically generated  by the model, 
        and does NOT represent the developer's viewpoint</span>
    </div>
  </div>
</template>

<script setup lang="ts">

import Setting from "./components/Setting.vue";
import FileUpload from "./components/FileUpload.vue";
import { ElMessage } from "element-plus";
import generateRandomId from "/@/utils/uuid";


useAsset('/path')
const input = ref('')
const router = useRouter()

const taskStore = useTaskStore()
const configStore = useConfigStore()

const agent = ref('');
const mode = ref('')

const settingChange = (val: any) => {
agent.value = val.agent;
mode.value = val.mode;
configStore.setNewtalkSettings({
  agent: val.agent,
  mode: val.mode
});
}

onMounted(() => {
useInitChatPreparation().then((res: any) => {
    if(!res || !res.data) {
      return;
    }
    const { data : { id } } = res;
    taskStore.setCurrentNewTalkId(id);
}).catch((err: any) => {
    console.log(err);
});
})


const sendMessage = (val: string) => {
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
  nextTick(() => {
    input.value = val;
  })
} else {
  
  configStore.setNewtalkSettings({
    agent: agent.value,
    mode: mode.value
  });
  configStore.setInput(val);

  router.push({
    name: 'newtalk',
    params: {
      mode: "new"
    }});
}
}
</script>

<style scoped lang="scss">

.config-cards {
display: flex;
flex-direction: column;
width: 100%;
gap: 24px;
padding: 34px calc(50% - 26vw) 60px;
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
