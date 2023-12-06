<template>
  <div ref="listRef" class="history-list flex-column">
    <template
      v-for="({ content, msgID, role, isLatest}, index) in currentHistoryTalk"
      :key="index">
      <TransitionGroup
        name="message"
        tag="div">
        <div v-if="role === 'USER'" class="flex-row input">
          <img src="@/assets/images/playground/userAvatar.svg" alt="message" />
          <div class="user-content-border">
            <span> {{ content }} </span>
          </div>
        </div>

        <div v-else-if="role === 'AI'" class="flex-row result typed-box">
          <img class="avatar round-corner-logo"  alt="logo"
            width="52" height="52" 
            src="@/assets/images/playground/main-logo-avatar.png"/>
          <div class="content">
            <Tab
              :ref="tabchildList"
              :conversationId="conversationId"
              :key="msgID"
              :mode="isAutoMode ? 'auto' : 'manual'"
              @disconnect="disConnectWebsocket"
              @runSubtask="RunNextSubtask"
              @runInner="RunNextinnerNode"
              :isLatest = "isLatest"
              :pageMode = "pageMode"
              :isLoading = "isSkeletonLoading"
            />
          </div>
          <div class="flex-row feedback-wrapper">
            <span v-if="isTaskCompleted" class="complete-tip">
              The Task is completed
            </span>
            <el-button 
              :icon="Share"
              v-if="canBeShared && isTaskCompleted"
              text
              type="primary"
              @click="handleTalkShare">
              share
            </el-button>
          </div>
        </div>
      </TransitionGroup>
    </template>
  </div>
  <div class="input-border flex-column" ref="inputBoxRef">
      <span
            v-if="workspaceFiles.length > 0"
            :class="[isFooterPanelCollapsed ? 
            'collapse-handle collapse-handle-unexpanded' : 
            'collapse-handle collapse-handle-expanded']"
            @click="handleCollapse">
          <span class="collapse-icon">
            <el-icon>
                <ArrowUpBold v-show="isFooterPanelCollapsed"/>
                <ArrowDownBold v-show="!isFooterPanelCollapsed"/>
            </el-icon>
          </span>
          <el-badge 
            :value="workspaceFilesNum"
            class="item"
            :type="isFooterPanelCollapsed ? 'info': 'primary' ">
            <span class="workspace-text">
              Workspace
            </span>
          </el-badge>
      </span>
    
    <div class="flex-row warning" v-if="isFooterPanelCollapsed">
      <a href="javascript:void(0);">
        Disclaimer: The content is probabilistically generated  by the model, 
        and does NOT represent the developer's viewpoint
      </a>
    </div>

    <div class="workspace-panel" v-else>
      <WorkSpace />
    </div>
  </div>
</template>

<script setup lang="ts">

import { Share, WarnTriangleFilled } from '@element-plus/icons-vue'
import { nextTick, ref, computed,  
watch, onBeforeUnmount, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { nanoid } from 'nanoid';
import generateRandomId from "/@/utils/uuid"
import debounce from '/@/utils/debounce';
import Tab from './components/Tab.vue'
import WorkSpace from './components/WorkSpace.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const configStore = useConfigStore()
const chatMsgInfoStore = useHistoryTalkStore()
const userStore = useUserStore()

// setup user info

const { userInfo } = storeToRefs(userStore)
userInfo.value = userStore.getUserInfo;
const user_id = userInfo?.value?.user_id as string;
const token = userInfo?.value?.token as string;

// page init setup
const pageMode = computed(() => {
const _mode = route.params.mode;
if(_mode) {
  return _mode as string;
} else {
  return '';
}
});

const currentNewTalkId = computed(() => taskStore.getCurrentNewTalkId);

const conversationId = computed(() => {
if(pageMode.value === 'playback' || pageMode.value === 'runshared') {
      const _id = route.params.id as string;
      if(!_id) { 
        router.push('/playground');
        console.log('chat.vue, line 133 ,  redirect to playground');
      }
      else { return _id; }
} else if(pageMode.value === 'recorder') {
      return route.params.id as string;
} else if(pageMode.value === 'new') {
      return currentNewTalkId.value;
} else {
      return '';
}
});

// set the User Question input

if(pageMode.value === "recorder") {
configStore.setInput('Record Playing');
}
conversationId.value && taskStore.setCurrentTaskId(conversationId.value);

// setup the talk sharing setting
const canBeShared = computed(() => (pageMode.value === "new" || pageMode.value === "playback"));

const handleTalkShare = () => {
const id = conversationId.value;
shareRequest(
  {
    interaction_id: id,
    user_id: userInfo.value?.user_id,
    token: userInfo.value?.token
  }
).then((res: any) => {
    console.log(res)
  }).catch((err: any) => {
    console.log(err)
  })
}

// setup the workspace files and workspace panel
const workspaceFilesNum = computed(() => taskStore.workspaceFiles.length)

const isFooterPanelCollapsed = ref(true)

const { workspaceFiles: workspaceFiles } = toRefs(taskStore);

const { 
input: newTalkInputText,
newtalkSettings: newtalkSettings,
filelist: fileListConfig
} = storeToRefs(configStore);

const inputBoxRef = ref<any>(null)

const handleCollapse = () => {
isFooterPanelCollapsed.value = !isFooterPanelCollapsed.value
if(!isFooterPanelCollapsed.value) {
  inputBoxRef && 
  inputBoxRef.value && 
  inputBoxRef.value.style.setProperty('padding-top', '0px')
} else {
  inputBoxRef && 
  inputBoxRef.value && 
  inputBoxRef.value.style.setProperty('padding-top', '2px')
}
}
// set up the tab ref and setting
const listRef = ref<Nullable<HTMLElement>>(null)
const refList = ref<Nullable<any>[]>([]);
const isSkeletonLoading = ref(true)

const tabchildList = (el: any) => {
el && refList.value.push(el)
}
const scrollToBottom = () => {
nextTick(() => {
  if (listRef.value) listRef.value!.scrollTop = listRef.value?.scrollHeight || 0
})
}

const handleStopLoading = () => {
isSkeletonLoading.value = false;
};

// setup auto mode
const isAutoModeMap = new Map([
['playback', true],
['recorder', true],
['runshared', true]
]) as Map<string, boolean>;

const isAutoMode = computed(() => {
if(pageMode.value === 'new') {
    return newtalkSettings.value?.mode === 'auto';
} else {
    return isAutoModeMap.get(pageMode.value) as boolean;
}
});

// taskStore.setAutoMode(isAutoModeMap.get(pageMode.value) as boolean);
// const { isAutoMode: isAutoMode } = storeToRefs(taskStore);
const {isCompleted: isTaskCompleted } = storeToRefs(taskStore);

// setup the websocket connection
let ws: WebSocket | null = null;

const BACKEND_URL = ( import.meta.env.VITE_BACKEND_URL as string ).replace(/\/api/, '');
const ws_protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws_host = BACKEND_URL.replace('https://', '').replace('http://', '');
const ws_origin = `${ ws_protocol }//${ ws_host }`;
const authStr = `${conversationId.value}?user_id=${user_id}&token=${token}`;

const pathMap = new Map([
['new', '/ws/base/'],
['playback', '/ws/replay/'],
['recorder', '/ws/recorder/'],
['runshared', '/ws/share/']
]) as Map<string, string>;

const recorder_dir = sessionStorage.getItem('rec');

if(recorder_dir) {
sessionStorage.removeItem('rec');
} // for record mode

const newTalkUrl = `${ ws_origin }${pathMap.get('new')}${ authStr }&description=${ newTalkInputText.value.substring(0, 26) }`;

const playbackUrl = `${ ws_origin }${pathMap.get('playback') }${ authStr }`;

const recordUrl = `${ ws_origin }${ pathMap.get('recorder') }${ authStr }&recorder_dir=${ recorder_dir }`;

const shareUrl = `${ ws_origin }${ pathMap.get('runshared') }${ authStr }`;

const stateMap = new Map([
[WebSocket.CONNECTING, 'CONNECTING'],
[WebSocket.OPEN, 'OPEN'],
[WebSocket.CLOSING, 'CLOSING'],
[WebSocket.CLOSED, 'CLOSED'],
]) as Map<number, string>;

const sendMsgViaWebsocket = (data: any) => {
if(ws && ws.readyState === WebSocket.OPEN) {
  const _data = typeof data === 'string' ? data : JSON.stringify(data);
  ws?.send(_data);
}
}

const closeWebsocketInstance = () => {
if(ws && ws.readyState === 1) { ws.close() }
}

const handleConnectFailNotification = (msg: string) => {
// taskStore.reset();
ElMessageBox.confirm( msg || 'Connection failed, please try again later.', 'Error',
  {
    type: 'error',
    icon: markRaw(WarnTriangleFilled),
  }
).then(() => {
  router.push('/playground')
}).catch(() => {
  router.push('/playground')
})
};

const disConnectWebsocket = () => {
const data = { type: "disconnect" }
sendMsgViaWebsocket(data);
closeWebsocketInstance();
ws = null;
};

const handleTaskCompletelyFinished = () => {
  taskStore.completeSubtask();
  closeWebsocketInstance();
  handleStopLoading();
  ElMessageBox({
    type: 'success',
    message: 'Your task is completed.'
  });
};

const pingKeepAlive = () => {
sendMsgViaWebsocket({ type: 'ping' });
};

const handleAlertError = (msg: string) => {
handleStopLoading();
return ElMessageBox.alert(msg, 'Error', {
    type: 'error',
    icon: markRaw(WarnTriangleFilled),
  },
)
}

const default_WS_Establish_Error_Handler = (e: any) => {
console.log("ws.onerror", e);
handleStopLoading();
}

const sendConnectResponse = () => {
const data = { type: 'connect'}
sendMsgViaWebsocket(data);
}

const wsMessageHandler = (data: any) => {
    const { status } = data;

    const tabRefArr = refList.value;
    let tabchild: any = null;
    if(tabRefArr && tabRefArr.length > 0) {
      tabchild = tabRefArr[tabRefArr.length - 1];
    }

    if(isTaskCompleted.value) return;

    if(data.success === false) {
      disConnectWebsocket();
      console.log('disconnect due to success is false');
      handleStopLoading();
      // taskStore.completeSubtask();
      handleAlertError(data.message).then(() => {
        // router.push('/playground')
      });
      return;
    }
    if(data.type === 'pong') {
      pingKeepAlive();
    }
    if(data.workspace_file_list && Array.isArray(data.workspace_file_list)) {
      taskStore.setWorkspaceFiles(data.workspace_file_list);
    }
    if(data.node_id) {
      taskStore.setLastStepId(data.node_id);
    }

    switch (status) {
        case 'start':
            taskStore.initializeSubtasks(data);
            break;

        case 'inner':
            taskStore.addInner(data);
            tabchild?.gotNewInnerNode();
            break;
        
        case 'subtask_submit':
            taskStore.addLastInner(data);
            tabchild?.gotNewInnerNode();

            break;

        case 'refinement':
            taskStore.addRefinementInfo(data);
            break;

        case 'subtask':
            taskStore.nextsubtask(data);
            tabchild?.jumpToNextSubtask();
            break;

        case 'finished':
            disConnectWebsocket();
            console.log('disconnect due to task finished');
            handleTaskCompletelyFinished();
            // resetRunConnectionOnce()
            break;

        case 'failed':
            handleStopLoading();
            handleConnectFailNotification(data?.message);
            disConnectWebsocket();
            console.log('disconnect due to task failed');
            // resetRunConnectionOnce()
            break;

        case 'connect':
            sendConnectResponse();
            break;

        default:
            break;
    }
};

const newTalkConnection = () => {
const query_params = {
  type: "data",
  args: 
  { 
    goal: newTalkInputText.value,
    // fileList 
  },
  agent: newtalkSettings.value?.agent,
  mode: newtalkSettings.value?.mode,
  file_list: fileListConfig.value
};
ws = new WebSocket( newTalkUrl );
ws.onmessage = (e) => { wsMessageHandler(JSON.parse(e.data)); }
ws.onerror = (e) => { default_WS_Establish_Error_Handler(e); }
ws.onopen = () => { sendMsgViaWebsocket(query_params);}
}

const runSharedConnection = () => {
taskStore.setAutoMode(true);
const query_params = { type: "shared"}
ws = new WebSocket(shareUrl);
ws.onmessage = (e) => { wsMessageHandler(JSON.parse(e.data)); }
ws.onerror = (e) => { default_WS_Establish_Error_Handler(e); }
ws.onopen = () => { sendMsgViaWebsocket(query_params);} 
}

const playbackConnection = () => {
const query_params = { type: "replay" }
taskStore.setAutoMode(true);
ws = new WebSocket(playbackUrl);
ws.onmessage = (e) => { wsMessageHandler(JSON.parse(e.data)); }
ws.onerror = (e) => { default_WS_Establish_Error_Handler(e); }
ws.onopen = () => { sendMsgViaWebsocket(query_params);}
}

const recordConnection = () => {
taskStore.setAutoMode(true);
const query_params = { type: "recorder"}
ws = new WebSocket(recordUrl);
ws.onmessage = (e) => { wsMessageHandler(JSON.parse(e.data)); }
ws.onerror = (e) => { default_WS_Establish_Error_Handler(e); }
ws.onopen = () => { sendMsgViaWebsocket(query_params);}
}

const RunConnection = () => {
console.log('run connection so we disconnect existing websocket');
disConnectWebsocket();
taskStore.reset();

switch(pageMode.value) {
  case 'playback':
    playbackConnection();
    break;

  case 'new':
    newTalkConnection();
    break;

  case 'recorder':
    recordConnection();
    break;

  case 'runshared':
    runSharedConnection();
    break;

  default:
    break;
}
}

// task and subtask running
const RunNextSubtask = (data: string) => {
const query_params = {
  type: "data",
  args: {
    goal: data,
  },
  agent: newtalkSettings.value?.agent,
  mode: newtalkSettings.value?.mode,
  node_id: taskStore.last_step_id || null,
};
sendMsgViaWebsocket(query_params);
};

const RunNextinnerNode = (data: any) => {
const query_params = {
  type: "data",
  args: {
    ... data,
  },
  agent: newtalkSettings.value?.agent,
  mode: newtalkSettings.value?.mode,
  node_id: taskStore.last_step_id || null,
};
sendMsgViaWebsocket(query_params);
};

// talks and history setup
const sharedTalksArr = computed(()  => chatMsgInfoStore.getSharedArr);
const historyTalksArr = computed(() => chatMsgInfoStore.getArrHistory);

const currentItem = computed(() => {
const _temp1 = historyTalksArr.value?.find(
    (item: any) => item.interaction_id === conversationId.value);
const _temp2 = sharedTalksArr.value?.find(
    (item: any) => item.interaction_id === conversationId.value);

switch(pageMode.value) {
    case 'playback':
      return {
        id: conversationId.value,
        text: (_temp1 && _temp1.parameters[0]) ? 
          _temp1.parameters[0]?.goal : 'PlayBack'
      }
    case 'new':
      return {
        id: conversationId.value,
        text: newTalkInputText.value || 'New Talk'
      }
    case 'recorder':
      return {
        id: conversationId.value,
        text: 'Run Record ' + recorder_dir
      }
    case 'runshared':
      return {
        id: conversationId.value,
        text: (_temp2 && _temp2.parameters[0]) ? 
           _temp2.parameters[0]?.goal : ('Run Shared Talk ' + conversationId.value)
      }
    default:
      return {
        id: conversationId.value,
        text: ''
      }
  }
});

const currentHistoryTalk = ref<any>([]);

watch(() => currentItem.value, (newVal, oldVal) => {
if(!newVal) {
  return;
}
currentHistoryTalk.value = [
  {
      content: newVal.text,
      msgID: nanoid(),
      parentMsgID: '',
      role: 'USER',
      isLatest: true
  },
  {
      content: '',
      msgID: newVal.id,
      parentMsgID: '',
      role: 'AI',
      isLatest: true
  }
]
}, { immediate: true });



watch(() => [pageMode.value, conversationId.value],
(newVal, oldVal) => {
  if(!pageMode.value || !conversationId.value) {
    router.push('/playground')
    return;
  }
  taskStore?.reset();
  taskStore?.setAutoMode(isAutoMode.value);
  debounce(function() {
    RunConnection();
  }, 1000)();
}
, { immediate: true });

onMounted(() => {
refList.value = [];
});

onBeforeUnmount(() => {
refList.value = [];
disConnectWebsocket();
console.log('chat unmounted so we disconnect existing websocket');
taskStore?.reset();
});

</script>

<style scoped lang="scss">
.history-list {
  display: flex;
  width: 100%;
  padding: 20px  calc(50vw - 130px - 32vw)  110px;
  background-color: rgb(236, 237, 245);
  overflow-y: auto;
  flex: 1 0 200px;
  .user-content-border{
    background: rgba(255,255,255,0.90);
    border-radius: 8px;
    width: 100%;
    padding: 12px 20px;
  }

  .input {
    font-family: MiSans-Medium;
    font-size: 14px;
    color: #1c2848;
    line-height: 24px;
    font-weight: 500;

    align-items: flex-start;
    gap: 10px;
    margin-block-end: 16px;
    white-space: pre-wrap;

    img {
      width: 26px;
      height: 26px;
    }
  }

  .result {
    margin-block-end: 10px;
    padding-bottom: 1px;

    position: relative;
    .content{
      width: 100%;
      border-radius: 8px;
    }
    .feedback-wrapper {
      width: calc(100% - 96px);
      position: absolute;
      top: 100%;
      right: 24px;
      gap: 12px;
      font-family: MiSans-Regular;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: flex-end;

      .complete-tip {
        color: #ccc;
        font-weight: 500;
      }

      .refresh {
        cursor: pointer;
        user-select: none;

        color: #3d4ac6;

        gap: 4px;

        margin-right: auto;
      }

      :deep(.feedback) {
        margin-left: auto;
      }
    }
  }
}

.typed-box {
  border-radius: 8px;
  gap: 10px;

  font-family: MiSans-Normal;
  font-size: 16px;
  color: #1c2848;
  line-height: 24px;

  .avatar {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border-radius: 4px;
  }
}
.input-border{
  z-index: 5;
  position: relative;
  left: 0px;
  bottom: 0;
  width: 100%;
  align-items: center;
  padding-top: 10px;
  background: rgb(240,241,250);
  box-shadow: inset 0 1px 3px 0 #FFFFFF;

  .collapse-handle-unexpanded {
    background: #fff;
    color: #666;
    .workspace-text {
      color: #666 !important;
    }
    .collapse-icon {
      color: #666;
    }
  }

  .collapse-handle-expanded {
    background: #666;
    color: #1C2848; 
    .workspace-text {
      color: #fff;
    }
    .collapse-icon {
      color: #fff;
    }
  }

  .collapse-handle {
    width: auto;
    height: 30px;
    padding: 5px 10px;
    font-family: PingFangSC-Regular;
    font-size: 12px;
    font-weight: 400;
    cursor: pointer;
    position: absolute;
    top: 0;
    right: 0;
    z-index: 999;
    border-radius: 8px 8px 0 0;
    transform: translateY(-100%);
    display: flex;
    align-items: flex-start;


    .workspace-text {
      font-size: 14px;
      color: #fff;
      font-weight: 700;
      padding-right: 10px;
      user-select: none;
    }
    
    .collapse-icon {
      margin-top: 3px;
      height: 20px;
      width: 20px;
      margin-right: 2px;
    }
  }

  .input-box {
    // width: 58vw;
    width: 100%;
    padding: 0 calc(50% - 26vw);
    // left: 50%;
    // transform: translateX(-50%);
  }
  .refresh-btn-border{
    display: flex;
    align-items: center;
    justify-content: center;
    .refresh-btn{
      height: 34px;
      width: 162px;
      background-color: #3D4AC6;
      border-radius: 8px;
      font-family: PingFangSC-Regular;
      font-size: 14px;
      color: #FFFFFF;
      line-height: 16px;
      font-weight: 400;
      cursor: pointer;
      .refresh-icon{
        height: 16px;
        width: 16px;
        margin-right: 14px;
      }
    }
    
  }

  .warning {
    margin-top: 32px;
    margin-bottom: 24px;
    width: 64vw;
    justify-content: center;
    font-family: PingFangSC-Regular;
    font-size: 12px;
    color: #dddddd;
    font-weight: 400;
    gap: 24px;
    text-align: center;
    user-select: none;
    
    a {
      color: #ddd;
      text-decoration: none;
    }
    a:active {
      color: #ddd;
    }
  }
}


.watermark {
pointer-events: none;
position: fixed;
width: calc(100% - 240px);
height: calc(100% - 120px);
top: 64px;
left: 240px;
bottom: 130px;
mix-blend-mode: darken;
z-index: 100;
}

.round-corner-logo{
border: none;
border-radius: 6px;
width: 52px;
height: 52px;
}

.workspace-panel {
height: 450px;
width: 100%;
background-color: #666;
padding-top: 3px;
}

</style>