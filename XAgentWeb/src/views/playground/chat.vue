<template>
  <section class="container-box flex-column">
    <div ref="listRef" class="history-list flex-column">
      <template
        v-for="({ content, msgID, role, isLatest}, index) in chatMsgInfo"
        :key="index"
      >
        <TransitionGroup
          name="message"
          tag="div"
          >
          <div v-if="role === 'USER'" class="flex-row input">
            <img src="@/assets/images/playground/userAvatar.svg" alt="message" />
            <div class="user-content-border">
              <span> {{ content }} </span>
            </div>
          </div>

          <div  v-else-if="role === 'AI'" class="flex-row result typed-box">
            <img class="avatar round-corner-logo"  alt="logo"
              width="52" height="52" 
              src="@/assets/images/playground/main-logo-avatar.png"/>
            <div class="content">
              <Tab 
                :ref="tabchildList"
                :conversationId="conversationId"
                :key="msgID"
                :mode="remSetting?.mode || 'auto'"
                @disconnect="disConnectWebsocket"
                @runSubtask="RunNextSubtask"
                @runInner="RunNextinnerNode"
                :isLatest = "isLatest"
                :pageMode = "pageMode"
                :isLoading = "isLoading"
              />
            </div>
            <div class="flex-row feedback-wrapper">
              <span v-if="isTaskCompleted" class="complete-tip">
                The Task is completed
              </span>
              <el-button 
                :icon="Share"
                v-if="canShare && isTaskCompleted"
                text
                type="primary"
                @click="onShare">
                share
              </el-button>
              <!-- <Feedback :data="{ content, msgID, role, conversationId, feedbackMsg, rating }" @evaluate-success="evaluateSuccess" /> -->
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
      <!-- <div class="input-box" v-show="chatMsgInfo.length <= 0">
        <TalkInput :is-progress="isShowTyped" @send-message="sendMessage" />
        <canvas class="watermark" style="opacity: 0;"></canvas>
      </div> -->
      <!-- <div
          class="input-box refresh-btn-border"
          v-show="chatMsgInfo.length > 0"
        >
        <el-button
          class="flex-row refresh-btn flex-center"
          @click="regenerate"
          disabled
          >
              <img class="refresh-icon"
                src ="@/assets/images/playground/refreshNew.svg"
                alt="refresh" />
              Regenerate
        </el-button>
      </div> -->
      
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
  </section>

</template>

<script setup lang="ts">

import hljs from 'highlight.js'
import MarkdownIt from 'markdown-it'
import { Share, WarnTriangleFilled } from '@element-plus/icons-vue'
import { nextTick, ref, watch } from 'vue'
import { onBeforeMount, onMounted, onBeforeUpdate, onUpdated, onUnmounted, onBeforeUnmount } from 'vue'
import { ChatMsgInfoInf, IChatRequest } from '/#/talk-type'
import { ElMessage, ElMessageBox } from 'element-plus'
import { nanoid } from 'nanoid';
import generateRandomId from "/@/utils/uuid"
import throttle from '/@/utils/throttle'
import Tab from './components/Tab.vue'
import WorkSpace from './components/WorkSpace.vue'

const { proxy: global_instance } = getCurrentInstance() as any

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const workspaceFilesNum = computed(() => taskStore.workspaceFiles.length)

const currentNewTalkId = computed(() => taskStore.getCurrentNewTalkId);

const {
    workspaceFiles: workspaceFiles
} = toRefs(taskStore);
// 根据conversionId查询历史对话

const chatMsgInfo = ref<ChatMsgInfoInf[]>([])

const isFooterPanelCollapsed = ref(true)
const inputBoxRef = ref<any>(null)
const isLoading = ref(true)

const BACKEND_URL = (
  import.meta.env.VITE_BACKEND_URL as string
  ).replace(/\/api/, '');

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

const configStore = useConfigStore()
const {
  filelist: fileListConfig,
} = storeToRefs(configStore)
const chatMsgInfoStore = useHistoryTalkStore()
const { currentInput, isRequestingAi } = storeToRefs(chatMsgInfoStore)

let ws: WebSocket | null = null;

let pageMode = computed(() => {
  if(!route.query || !route.query.mode) {
    if(route.params && route.params.mode)
    {
      return route.params.mode as string;
    }
  }
  return route.query.mode as string || '';
}); // Redirected from other page, playback, review, or start a new conversation


if(pageMode.value === "recorder") {
  chatMsgInfoStore.setCurrentInput('Record Playing');
}

console.log("route.params = ", route.params)

let conversationId = computed(() => {
  switch(pageMode.value) {
      case 'playback':
        return route.params.id as string || '';
        break;

      case 'runshared':
        return route.params.id as string || '';
        break;

      case 'review':
        return route.query.id as string || '';
        break;

      case 'new':
        return currentNewTalkId.value as string || generateRandomId();
        break;

      case 'recorder':
        return route.params.id as string || generateRandomId();
        break;

      default:
        // router.push('/playground')
        return '';
        break;
    }
})


const canShare = computed(() => {
    return pageMode.value === "new" || pageMode.value === "playback";
})


const refList = ref<Nullable<any>[]>([]);
const tabchildList = (el: any) => {
  if(el) {
    refList.value.push(el);
  }
};

// if(!route.params.mode && !route.query?.mode) {
//   router.push('/playground')
// }

const taskInfo = storeToRefs(taskStore);

const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)
userInfo.value = userStore.getUserInfo;

conversationId.value && taskStore.setCurrentTaskId(conversationId.value);

const {
  historyArr : ChatHistoryArr
}= storeToRefs(chatMsgInfoStore);

const sharedTalksArr = computed(()  => chatMsgInfoStore.getSharedArr);

const currentItem = computed(() => {
  const _chat_history_arr = ChatHistoryArr?.value || [];
  const _shared_talks_arr = sharedTalksArr?.value || []
  const arr = pageMode.value === 'runshared' ? _shared_talks_arr : _chat_history_arr;
  return arr?.find(
    (item: any) => item.interaction_id === conversationId.value);
});

chatMsgInfo.value = [
  {
    content: currentItem.value?.parameters[0]?.goal || chatMsgInfoStore.getCurrentInput,
    msgID: nanoid(),
    parentMsgID: '',
    role: 'USER',
    isLatest: true
  },
  {
    content: '',
    msgID: currentItem.value?.interaction_id || '',
    parentMsgID: '',
    role: 'AI',
    isLatest: true
  }
]

// 判断当前会话是不是历史会话 如果不是的话，则设置获取没有设置conversationId的记忆设置
const setting = chatMsgInfoStore.getSetting(conversationId.value)
const remSetting = chatMsgInfoStore.getSetting('config')


taskStore.setAutoMode(remSetting?.mode === 'auto');

const {
    isCompleted: isTaskCompleted
  } = storeToRefs(taskStore);

const {
    subtasks: subTasks
  } = storeToRefs(taskStore);
  

const stateMap = new Map([
  [WebSocket.CONNECTING, 'CONNECTING'],
  [WebSocket.OPEN, 'OPEN'],
  [WebSocket.CLOSING, 'CLOSING'],
  [WebSocket.CLOSED, 'CLOSED'],
]) as Map<number, string>;

// TODo: when ws closed , stop loading;

const handleConnectFailNotification = (msg: string) => {
  taskStore.reset();
  ElMessageBox.confirm(
    msg || 'Connection failed, please try again later.',
    'Error',
    {
      type: 'error',
      icon: markRaw(WarnTriangleFilled),
    }
  )
};

const handleFinish = () => {
    taskStore.completeSubtask();
    if(ws && ws.readyState === 1) {
        ws.close();
    }
    ElMessageBox({
      type: 'success',
      message: 'Your task is completed.'
    })
};
const handleFailed = () => {
  taskStore.completeSubtask();
}
const RunNextSubtask = (data: string) => {
  const query_params = JSON.stringify({
    type: "data",
    args: {
      goal: data,
    },
    agent: remSetting?.agent,
    mode: remSetting?.mode,
    node_id: taskStore.last_step_id || null,
  });
  if(ws && ws.readyState === WebSocket.OPEN) {
    ws?.send(query_params);
  }
};


const user_id = userInfo?.value?.user_id as string;
const token = userInfo?.value?.token as string;
const chatIdFromRoute = computed(() => {
  return (route.params.id);
});

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

const recorder_dir = sessionStorage.getItem('rec');

if(recorder_dir) {
  sessionStorage.removeItem('rec');
}

const plainUrl = `${ protocol }//${ 
    BACKEND_URL.replace('https://', '')
    .replace('http://', '')
  }/ws/base/${
    conversationId.value
  }?user_id=${
    user_id
  }&token=${
    token
  }&description=${
currentInput.value.substring(0, 26)}`;

const playbackUrl = `${ protocol }//${
  BACKEND_URL.replace('https://', '').replace('http://', '')
}/ws/replay/${
  conversationId.value
}?user_id=${user_id}&token=${token}`;

const recordUrl = `${ protocol }//${ BACKEND_URL.replace('https://', '').replace('http://', '')
}/ws/recorder/${
  conversationId.value
}?user_id=${user_id}&token=${token}&recorder_dir=${recorder_dir}`;

const runShareUrl = `${ protocol }//${
  BACKEND_URL.replace('https://', '').replace('http://', '')
}/ws/share/${
  conversationId.value
}?user_id=${user_id}&token=${token}`;

const RunNextinnerNode = (data: any) => {
  const query_params = JSON.stringify({
    type: "data",
    args: {
      ...data,
    },
    agent: remSetting?.agent,
    mode: remSetting?.mode,
    node_id: taskStore.last_step_id || null,
  });

  if(ws && ws.readyState === WebSocket.OPEN) {
    ws?.send(query_params);
  }
};

const pingKeepAlive = () => {
  const ping = JSON.stringify({
    type: 'ping'
  });
  if(ws && ws.readyState === WebSocket.OPEN) {
    ws?.send(ping);
  }
};

const handleStopLoading = () => {
  isLoading.value = false;
};

const disConnectWebsocket = () => {
  const data = {
    type: "disconnect"
  }
  if(ws && ws.readyState === WebSocket.OPEN) {
    ws?.send(JSON.stringify(data));
  }
  if(ws && ws.readyState === 1) {
    ws.close();
  }
  ws = null;
}

const scrollToBottom = () => {
  nextTick(() => {
    if (listRef.value) listRef.value!.scrollTop = listRef.value?.scrollHeight || 0
  })
}

const sendConnectType = () => {
  const data = {
    type: 'connect',
  }
  if(ws && ws.readyState === WebSocket.OPEN) {
    ws?.send(JSON.stringify(data));
  }
}

const wsMessageHandler = (data: any) => {
      const { status } = data;

      // if(isCompleted.value) {
      //   return;
      // }
      const tabRefArr = refList.value;
      const tabchild = tabRefArr[tabRefArr.length - 1];

      if(data.success === false) {
        ElMessageBox.alert(
          data.message,
          'Error',
          {
            type: 'error',
            icon: markRaw(WarnTriangleFilled),
          },
        )
        // Stop the skeleton loading
        // taskStore.completeSubtask();

        disConnectWebsocket();
        // router.push('/playground')
        return;
      }

      if(data.type = 'pong') {
        pingKeepAlive();
      }

      if(data.workspace_file_list && Array.isArray(data.workspace_file_list)) {
        taskStore.setWorkspaceFiles(data.workspace_file_list);
      }

      data.node_id && taskStore.setLastStepId(data.node_id);

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
              handleFinish();
              disConnectWebsocket();
              resetRunConnectionOnce()
              break;

          case 'failed':
              handleStopLoading();
              handleConnectFailNotification(data?.message);
              disConnectWebsocket();
              resetRunConnectionOnce()
              break;

          case 'connect':
              sendConnectType();
              break;

          default:
              break;
      }
};

const newTalkConnection = () => {
  taskStore.reset();
  const query_params = {
    type: "data",
    args: {
      goal: currentInput.value,
      // fileList 
    },
    agent: remSetting?.agent,
    mode: remSetting?.mode,
    file_list: fileListConfig.value
  };
  ws = new WebSocket(plainUrl );
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    wsMessageHandler(data);
  }
  ws.onerror = (e) => {
    console.log("ws.onerror");
  }
  ws.onopen = () => {
    if(ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(query_params));
    }
  }
}

// Input answer
const sendMessage = async (val: string) => {
  if (!val) return
  chatMsgInfoStore.setCurrentInput(val)
  chatMsgInfo.value = [
      {
        content: val,
        msgID: nanoid(),
        parentMsgID: '',
        role: 'USER',
        isLatest: true
      },
      {
        content: '',
        msgID: nanoid(),
        parentMsgID: '',
        role: 'AI',
        isLatest: true
      }
  ]
  // const inputMsg: ChatMsgInfoInf = {
  //   role: 'USER',
  //   content: currentInput.value,
  //   msgID: nanoid(),
  //   parentMsgID: chatMsgInfo.value.at(-1)?.msgID || '',
  //   childrenIds: [],
  // }
  // const lastChat = chatMsgInfo.value.at(-1)
  // if (lastChat) {
  //   lastChat.childrenIds = [...(lastChat.childrenIds as string[] || []), inputMsg.msgID]
  // }
  // chatMsgInfo.value.push(inputMsg);

  // if (chatMsgInfo.value.length === 1) {
  //   chatMsgInfoStore.setHistoryChat(conversationId.value, inputMsg)
  // } else {
  //   chatMsgInfoStore.pushHistoryChat(conversationId.value, inputMsg)
  // }

  nextTick(() => (listRef.value!.scrollTop = listRef.value?.scrollHeight || 0))
  // currentInput.value = ''

  // await queryAnswer().finally(() => chatMsgInfoStore.setisShouldRefreshHistory(true))
  return Promise.resolve()
}


const onShare = () => {
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

const runSharedConnection = () => {
  if(!conversationId.value) {
    console.log("conversationId.value is null");
    return;
  }
  const query_params = {
      type: "shared"
  }
  taskStore.setAutoMode(true);
  ws = new WebSocket(runShareUrl);
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    wsMessageHandler(data);
  }
  ws.onerror = (e) => {
    console.log("ws.onerror");
  }
  ws.onopen = () => {
    if(chatIdFromRoute.value  && ws && ws.readyState === WebSocket.OPEN) {
      ws?.send(JSON.stringify(query_params));
    }
  }
}

const playbackConnection = () => {
  if(!conversationId.value) {
    console.log("conversationId.value is null");
    return;
  }
  const query_params = {
      type: "replay"
  }
  taskStore.setAutoMode(true);
  ws = new WebSocket(playbackUrl);
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    wsMessageHandler(data);
  }
  ws.onerror = (e) => {
    console.log("ws.onerror");
  }
  ws.onopen = () => {
    if(chatIdFromRoute.value  && ws && ws.readyState === WebSocket.OPEN) {
      ws?.send(JSON.stringify(query_params));
    }
  }
}

const recordConnection = () => {
  taskStore.setAutoMode(true);
  const query_params = {
      type: "recorder"
  }
  ws = new WebSocket(recordUrl);
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    wsMessageHandler(data);
  }
  ws.onerror = (e) => {
    console.log("ws.onerror");
  }
  ws.onopen = () => {
    if(ws && ws.readyState === WebSocket.OPEN) {
      ws?.send(JSON.stringify(query_params));
    }
  }
}


const RunConnection = () => {
  disConnectWebsocket();
  switch(pageMode.value) {
    case 'playback':
      playbackConnection();
      break;

    case 'review':
      // newTalkConnection();
      break;

    case 'new':
      const input = currentInput.value;
      if (input) {
        newTalkConnection();
        sendMessage(input)
      } else {
        router.push('/playground')
      }
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
const isShowRunConnectionOnce = ref(false)
let RunConnectionOnce = function() {
  RunConnection();
  if (pageMode.value == 'new' || pageMode.value == 'recorder') {
    
    RunConnectionOnce = function () {
      if (!isShowRunConnectionOnce.value) {
        isShowRunConnectionOnce.value = true
        ElMessageBox.alert(
          'The task is running, please wait!',
          'Error',
          {
            type: 'error',
            icon: markRaw(WarnTriangleFilled),
            
          },
          
        ).then(() => {
          isShowRunConnectionOnce.value = false
        })
        .catch(() => {
          isShowRunConnectionOnce.value = false
        })
      }
      
    }
    
  }
}
// task Complete And Reset RunConnectionOnce
const resetRunConnectionOnce = () => {
  RunConnectionOnce = () => {
    RunConnection();
  }
}
watch(() => currentItem.value,
  (newVal, oldVal) => {

    console.log("currentItem.value = ", currentItem.value);
    if(!currentItem.value) {
      return;
    }
    RunConnectionOnce();
    chatMsgInfo.value = [
      {
        content: currentItem.value?.parameters[0]?.goal || chatMsgInfoStore.getCurrentInput,
        msgID: nanoid(),
        parentMsgID: '',
        role: 'USER',
        isLatest: true
      },
      {
        content: '',
        msgID: currentItem.value?.interaction_id || '',
        parentMsgID: '',
        role: 'AI',
        isLatest: true
      }
    ]
  },
  {
    immediate: true
  }
);

onUnmounted(() => {
  disConnectWebsocket();
  chatMsgInfo.value = [];
  taskStore.reset();
});

const md = new MarkdownIt({
  html: true,
  // breaks: true,
  linkify: true,
  highlight: function (str, lang) {
    const div = document.createElement('div')
    div.id = conversationId.value
    div.classList.add('copy-btn')
    div.dataset.clipboardAction = 'copy'
    div.dataset.clipboardTarget = `#copy${nanoid()}`
    div.innerText = 'Copy'

    let html = ''
    const language = hljs.getLanguage(lang) ? lang : 'python'
    const code = hljs.highlight(str, { language }).value

    div.addEventListener('click', (e: any) => {
      console.log(e)
    })

    try {
      html = html + code
    } catch {}
    return `<pre><code class="hljs language-${lang}">${html}</code></pre>`
  },
  langPrefix: 'hljs language-',
})


const isShowTyped = ref(false)
const isTypedStop = ref(true)


watch(() =>[ route.params.id , route.query.id, route.query.mode],
  (newVal, oldVal) => {

    taskStore.reset();
    console.log("changed route,  route = ", newVal);

    // if(!pageMode.value) {
    //   router.push('/playground')
    //   return;
    // }

    if(pageMode.value === 'playback' || pageMode.value === 'review' || pageMode.value === 'record') {
        taskStore.reset();

        if(pageMode.value === 'playback') {
          taskStore.setAutoMode(true);
        } else {
          taskStore.setAutoMode(false);
          taskStore.completeSubtask();
        }

        // if(!conversationId.value) {
        //   router.push('/playground')
        //   return;
        // }
        // if(!currentItem.value) {
        //   router.push('/playground')
        //   return;
        // }

        chatMsgInfo.value = [
          {
            content: currentItem.value?.parameters[0]?.goal || chatMsgInfoStore.getCurrentInput,
            msgID: nanoid(),
            parentMsgID: '',
            role: 'USER',
            isLatest: true
          },
          {
            content: '',
            msgID: currentItem.value?.interaction_id,
            parentMsgID: '',
            role: 'AI',
            isLatest: true
          }
        ]
    }
    RunConnectionOnce();
    nextTick(() => {
      if (listRef.value) listRef.value!.scrollTop = listRef.value?.scrollHeight || 0
    })
    // conversationId.value = newVal.id  as string
    // queryChatInfo(newVal.id  as string).finally(() => {
    //   if (isNew) {
    //     isShowTyped.value = false

    //   } else {

    //     if (isRequestingAi.value) {
    //       isShowTyped.value = true
    //     } else {
    //       isShowTyped.value = !isTypedStop.value
    //     }
    //   }
    //   nextTick(() => {
    //     if (listRef.value) listRef.value!.scrollTop = listRef.value?.scrollHeight || 0
    //   })
    // })
  },
  {
    immediate: true
  }
)

// const queryChatInfo = async (id: string) => {
//   if (!id) return
//   const {data: res} = await getDataApi({ convId: id })

//   // 此APi在正式环境不可用
//   // return  RequestData


//   const useMessage = res.data.msgInfos.find((cmp: any) => {
//     return cmp.role === 'USER'
//   })
//   // currentInput.value = useMessage.content
//   // const res = {...RequestData}
//   // console.log(RequestData)
//   // to
//   const newRes = {...res, ...{dataNew: {
//     setting: {
//       mode: 'manual',
//       agent: 'Data agent',
//       plugins: ['1'],
//       temperature: new Date().getTime(),
//     }
//   }}}

//   // if (!res?.data?.msgInfos[0]) {
//   //   router.push('/playground')
//   //   return
//   // }
//   const msgArr: any[] = res?.data?.msgInfos

//   chatMsgInfoStore.setHistoryChat(id, msgArr)
//   chatMsgInfoStore.setSetting(id, newRes.dataNew.setting)
//   const arr = msgArr.reduce((prev, current, index) => {
//     prev[current.msgID] = msgArr.filter((msgItem) => msgItem.parentMsgID === current.msgID)?.map((item) => item.msgID)
//     return prev
//   }, {})

//   const newArr: any[] = []
//   msgArr.forEach((item, index) => {
//     item.content_html = md.render(item.content)
//     item.childrenIds = arr[item.msgID]
//     if (index === 0) {
//       newArr.push(item)
//     }
//     const parentMsg = msgArr.find((msgItem) => msgItem.msgID === newArr.at(-1).parentMsgID)
//     if (!parentMsg) return
//     newArr.push(parentMsg)
//   })

//   chatMsgInfo.value = newArr.reverse().slice(0, 2)

//   nextTick(() => (listRef.value!.scrollTop = listRef.value?.scrollHeight || 0))
// }

// 增加水印
// const userInfoStore = useUserStore()
// const { userInfo } = storeToRefs(userInfoStore)
// onMounted(() => useInitWaterMark('.watermark', userInfo.value?.user_id + ''))

const listRef = ref<Nullable<HTMLElement>>(null)
const wormText = (params: IChatRequest, {tasks, costTime, msgId }: {tasks: any; costTime: number; msgId: string }, refresh: boolean) => {
  const run = async () => {
    isShowTyped.value = false
    isTypedStop.value = true
    // TODO: 赋值ID
    const newChat: ChatMsgInfoInf = {
      msgID: msgId,
      content: '',
      parentMsgID: params.chatMessage.at(-1)!.id || '',
      role: 'AI',
      costTimeMilli: costTime,
      subTasks: [],
      isLatest: true
      // Is the current inner the latest message
    }
    chatMsgInfo.value.forEach((item) => {
      item.isLatest = false
    })
    chatMsgInfo.value.at(-1)?.childrenIds?.push(msgId)
    chatMsgInfo.value.push(newChat)

    chatMsgInfoStore.pushHistoryChat(params.conversationId, newChat)

    nextTick(() => {
      if (listRef.value) listRef.value!.scrollTop = listRef.value?.scrollHeight || 0
    })
  }

  isTypedStop.value = false
  run()
}


// Regenerate the message
const regenerate = () => {
  const input = currentInput.value
  sendMessage(input)
}

// 初次加载逻辑
// if (route.query.id) {
//   chatMsgInfoStore.setisShouldRefreshHistory(false)
//   queryChatInfo(route.query.id as string)
// } 
// const strFragment = reactive<Array<{ text: string; isEnd: boolean; isProgress: boolean; id: string }>>([])
// 请求AI结果
// async function queryAnswer(refresh?: string): Promise<void> {  
//   if (isShowTyped.value) return
//   isShowTyped.value = true
//   isRequestingAi.value = true

//   const chatMessage: Array<HistoryListInf> = chatMsgInfo.value?.map(
//     ({ role, content, msgID, parentMsgID, costTimeMilli }: ChatMsgInfoInf, index) => {
//       return {
//         content: { pairs: content, type: 'TEXT', costTime: costTimeMilli || 0 },
//         id: msgID,
//         role,
//         parentMsgID: parentMsgID || '',
//       }
//     }
//   )

//   const params: IChatRequest = {
//     chatMessage: chatMessage.slice(-10),
//     conversationId: conversationId.value,
//     parentMessageId: '',
//     generateType: !!refresh ? 'REGENERATE' : 'NORMAL',
//     setting: route.query.id ? setting : remSetting,
//   }

//   lastConversionId.value = unref(conversationId)
//   const {data: res} = await refreshDataApi(params)
//   // 此APi在正式环境不可用
//     //  return refreshAIData
//   isRequestingAi.value = false
//   lastConversionId.value = ''
//   if (res?.code === 0) {
//     // const tasks = res?.data?.subTasks || []
//     const tasks = res?.data?.subTasks || []
//     const costTime = res?.data?.costTimeMillis
//     // const msgId = res?.data?.msgId
//     const msgId = new Date().getTime() + '' // todo id不同  用来辨别
//     if (params.conversationId !== conversationId.value) {
//       isShowTyped.value = !isTypedStop.value
//     } else {
//       isShowTyped.value = true
//       wormText(params, {tasks, costTime, msgId}, !!refresh)
//     }
//   } else {
//     ElMessage({ type: 'error', message: res?.message })
//   }
// }

// 重新生成
// const refreshAnswer = ({ msgID }: { msgID: string }) => {
//   // 存储操作
//   useFeedbackRequest({ messageId: msgID, conversationId: conversationId.value, rating: 'THUMBS_NO', feedbackAction: 'REGENERATE' })
//   // 删除最后一个回答
//   chatMsgInfo.value.pop()
//   queryAnswer('refresh')
// }

// 反馈成功
// const evaluateSuccess = ({ feedbackMsg, messageId, rating }: { feedbackMsg: string; messageId: string; rating: feedbackRating }) => {
//   const currentMessage = chatMsgInfo.value.find((item) => item.msgID === messageId)
//   if (currentMessage) {
//     currentMessage.rating = rating
//     currentMessage.feedbackMsg = feedbackMsg
//   }
// }

// const switchMsg = (val: { index: number; lastId: string; currentId: string; conversationId: string }) => {
//   const historyChat = chatMsgInfoStore.getHistoryChat(val.conversationId)

//   const lastChatIndex = chatMsgInfo.value.findIndex((item) => item.msgID === val.lastId)
//   const lastChat = chatMsgInfo.value.slice(0, lastChatIndex)
//   const currentChat = historyChat.find((item: ChatMsgInfoInf) => item.msgID === val.currentId)

//   let followChat: ChatMsgInfoInf[] = []

//   const findChat = (msgID: string) => {
//     const chat = historyChat.find((item: ChatMsgInfoInf) => item.parentMsgID === msgID)
//     if (chat) {
//       followChat.push(chat)
//       findChat(chat.msgID)
//     }
//   }
//   findChat(val.currentId)
//   if (followChat[0]) {
//     chatMsgInfo.value = [...lastChat, currentChat, ...followChat]
//   } else {
//     chatMsgInfo.value = [...lastChat, currentChat]
//   }

//   nextTick(() => {
//     if (followChat.length === 0) {
//       if (listRef.value) listRef.value!.scrollTop = listRef.value?.scrollHeight || 0
//     }
//   })
// }
</script>

<style scoped lang="scss">
.container-box {
  position: relative;
  background-color: rgb(236, 237, 245);
  padding: 20px 0 0;
  gap: 24px;
  .history-list {
    display: flex;
    // width: 58vw;
    padding: 0  calc(50vw - 130px - 32vw)  110px;
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