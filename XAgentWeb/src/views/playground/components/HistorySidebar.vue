<template>
  <section class="sidebar">

    <div class="logo_name_border flex-column">
      <img class="logo" alt="" draggable="false"
        src="@/assets/images/playground/main-logo-6-5.png" 
          width="144" height="120"
        />
      <img class="name" src="@/assets/images/playground/name-logo.png" draggable="false"
        alt="" width="128" height="35"/>
    </div>

    <div 
        class="new-talk flex-row flex-center"
        @click="createNewTalk"
        v-if="isBetaUser">
      <span>New Talk</span>
    </div>

    <div class="history-list flex-column" 
        v-if="isBetaUser"
      >
      <div
        v-for="(item, index) in historyTalkArr"
        :key="item.interaction_id"
        class="history-item flex-row"
        :class="{ active: item.interaction_id === route.query.id }"
      >
        <img src="@/assets/images/playground/qp.svg" alt="" class="icon" />
        <span class="ellipsis"
               @click="switchToConversation(item)">
            {{ item.description }}
        </span>

        <span class="delete_btn flex-row" >
          <span class="playback-icon"
                title="Run the task"  
                @click="playbackItem(item, index)">
            <VideoPlay />
          </span>
          <el-popconfirm
            width="fit-content"
            popper-class="delete-tip"
            confirm-button-text="Confirm"
            cancel-button-text="Cancel"
            :hide-icon="true"
            :hide-after="0"
            placement="top"
            title="Are you sure to delete this conversation? This operation cannot be undone."
            @confirm="deleteHistory(item, index)"
          >
            <template #reference>
              <span>
                <IconDelete />
              </span>
            </template>
          </el-popconfirm>
        </span>
      </div>

      <div v-if="historyTalkArr.length <= 0 && !loading" class="no-data flex-column flex-center">
        <img src="@/assets/images/playground/no-history.svg" alt="" />
        <span>
          No content for now
        </span>
        <span>
          Start a new conversation to experience
        </span>
      </div>

      <div v-if="loading" 
        class="no-data loading flex-column flex-center"
        data-loading="Data Loading..."></div>
    </div>
    
    <div class="clear-btn-border flex-center">
      <el-dropdown 
        placement="top"
        trigger="click"
        class="clear-btn flex-row flex-center"
        @command="handleCommand"
      >
        <span class="el-dropdown-link">
          <el-icon class="el-icon--left">
            <Setting />
          </el-icon>
            Settings
        </span>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="blog">
              <div class="menu-item-row">
                <span>
                  Blog
                </span>
              </div>
            </el-dropdown-item>
          </el-dropdown-menu>

          <el-divider :style="{padding: '0px',margin: '0px'}" v-if="isBetaUser"></el-divider>

          <el-dropdown-menu>
            <el-dropdown-item command="community">
              <div class="menu-item-row">
                <span>
                  Community
                </span>
              </div>
            </el-dropdown-item>
          </el-dropdown-menu>

          <!-- 暂时关闭 -->
          <!-- <el-divider :style="{padding: '0px',margin: '0px'}" v-if="isBetaUser"></el-divider>
          
          <el-dropdown-menu v-if="isBetaUser">
            <el-dropdown-item command="runrecord">
              <div class="menu-item-row">
                <span>
                  Run Recorder 
                </span>
              </div>
            </el-dropdown-item>
          </el-dropdown-menu> -->

          <el-divider :style="{padding: '0px',margin: '0px'}" v-if="isBetaUser"></el-divider>
          
          <el-dropdown-menu>
            <el-dropdown-item command="logout">
              <div class="menu-item-row">
                <span>
                  <svg t="1698909989767" class="icon"
                    viewBox="0 0 1024 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg" p-id="4227"
                    width="15px" height="15px"><path d="M85.333333 256a85.333333 85.333333 0 0 1 85.333334-85.333333h384a85.333333 85.333333 0 0 1 85.333333 85.333333v85.333333a42.666667 42.666667 0 1 1-85.333333 0V256H170.666667v512h384v-85.333333a42.666667 42.666667 0 1 1 85.333333 0v85.333333a85.333333 85.333333 0 0 1-85.333333 85.333333H170.666667a85.333333 85.333333 0 0 1-85.333334-85.333333V256z m652.501334 97.834667a42.666667 42.666667 0 0 1 60.330666 0l128 128a42.666667 42.666667 0 0 1 0 60.330666l-128 128a42.666667 42.666667 0 0 1-60.330666-60.330666L793.002667 554.666667H384a42.666667 42.666667 0 1 1 0-85.333334h409.002667l-55.168-55.168a42.666667 42.666667 0 0 1 0-60.330666z" fill="#8a8a8a" p-id="4228"></path></svg>
                </span>
                <span>
                  Log out
                </span>
              </div>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </section>
</template>

<script setup lang="ts">

import { ElMessage, ElMessageBox } from 'element-plus';
import generateRandomId from "/@/utils/uuid";
// import AppComp from '/@/react-js/components/App.jsx';

const loading = ref(true)
const route = useRoute()
const router = useRouter()

// const reactContainer = ref(null);

const userStore = useUserStore()
const authStore = useAuthStore()
const chatMsgInfoStore = useHistoryTalkStore()
const historyTalkArr = computed(()  => chatMsgInfoStore.getArrHistory);
const { userInfo: userInfo } = storeToRefs(userStore)

const isBetaUser = true;

const { isRequestingAi } = storeToRefs(chatMsgInfoStore)
const emits = defineEmits<{ (e: 'createTalk'): void; (e: 'clear'): void }>();

const createNewTalk = () => {
  if (isRequestingAi.value) {
    ElMessage({
      type: 'warning', 
      message: 'You have a request in progress, please try again later'
    })
    return
  }
  router.push('/playground');
}

onMounted(() => {
  queryHistoryData();
  // renderReactCompInsideVue(AppComp, reactContainer.value);
});

const queryHistoryData = () => {
  loading.value = true
  useHistoryListRequest().then((res) => {
      const list = res?.data?.rows || []
      chatMsgInfoStore.setHistoryArr(list);
    })
    .finally(() => {
      loading.value = false
    })
}

// watchEffect(() => {
//   if (isShouldRefreshHistory.value) queryHistoryData()
// })

const switchToConversation =  (item: any) => {
  // if (isRequestingAi.value) {
  //   ElMessage({ 
  //       type: 'warning',
  //       message: 'You have a request in progress, please try again later'
  //   });
  //   return
  // }
  // console.log("switch to conversation", item);

  // router.push({ 
  //   path: '/playground/chat', 
  //   query: {
  //     id: item.interaction_id,
  //     mode: "review"
  //   }
  // })

  return ;
}

const deleteHistory = async (item: any , index: number) => {

  // const conversationId = route.query.id

  // // await useDeleteHistoryRequest({ id: [item.id] })
  // // queryHistoryData()

  // if (conversationId && conversationId === item.id) {
  //   router.push('/playground')
  // } else if (!conversationId && item.id) {
  //   router.push('/playground')
  // }

  await useDeleteHistoryRequest({
    interaction_id: item.interaction_id
  });
  queryHistoryData()
}

const playbackItem = (item: any, index: number) => {
  router.replace({
    name: 'viewTalk',
    params: { 
      id: item.interaction_id,
      mode: 'playback'
    }
  });
}

const Logout = () => {
  const tips_str_en = 'Are you sure to log out?'
  const cancel_str_en = 'Cancel'
  const confirm_str_en = 'Confirm'

  ElMessageBox.confirm(tips_str_en, {
    customClass: 'delete-tip',
    cancelButtonText: cancel_str_en,
    confirmButtonText: confirm_str_en,
  }).then(() => {
    authStore.clearLoginState()
    userStore.clearUserInfo()
  }).then(() => {
    router.push('/login');
    window.location.reload();
    ElMessage({
      type: 'success',
      message: 'Log out successfully'
    });
  });
}

const handleShare = () => {
  // router.push({ path: '/share' })
  window.open('https://x-agent.net/', '_blank');
}

const handleRecord = () => {
  ElMessageBox.prompt('Please enter a record file path:', 'REC', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    inputPattern: /\S+/,
    inputErrorMessage: 'Invalid String',
  })
  .then(({ value }) => {
    if (value) {
      sessionStorage.setItem('rec', value);
      router.push({
        name: 'NewTalk',
        params: {
          mode: "recorder",
          id: generateRandomId(),
        }});
    }
  })
  .catch(() => {
    ElMessage({
      type: 'info',
      message: 'Cancelled',
    })
  })
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'logout':
      Logout();
      break;

    case 'runrecord':
      handleRecord();
      break;

    case 'community':
      handleShare();
      break;

    case 'blog':
    window.open('https://blog.x-agent.net/', '_blank');
      break;

    default:
      break;
  }
}

const clearHistory = () => {

  const tips_str_en = 'Are you sure to clear all the conversations? This operation cannot be undone.'
  const cancel_str_en = 'Cancel'
  const confirm_str_en = 'Confirm'

  ElMessageBox.confirm(tips_str_en, {
    customClass: 'delete-tip',
    cancelButtonText: cancel_str_en,
    confirmButtonText: confirm_str_en,
  }).then(() => {
    // async () => {
    // const ids: string[] = history.value.map((item) => item.id)
    // const res = await useDeleteHistoryRequest({ convIds: ids })
    // if (res?.code === 0) {
    //   history.value = []
    //   historyTalkStore.clearHistory()
    //   router.push('/playground')
    // }
      router.push('/share');
    });
  }
</script>

<style scoped lang="scss">
.sidebar {
  // background-image: linear-gradient(180deg, #f4f3f8 0%, #eaedf6 100%);
  background-color: #fff;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;

  .logo_name_border{
    margin: 40px 0px 32px 0px;
    align-items: center;
    user-select: none;
    .logo{
      height: 120px;
      width: 144px;
      margin-bottom: 16px;
    }
  }
  .new-talk {
    cursor: pointer;
    user-select: none;
    background: #3D4AC6;
    border-radius: 8px;
    font-family: MiSans-Regular;
    font-size: 15px;
    height: 40px;
    flex-basis: 40px;
    color: #FFFFFF;
    text-align: center;
    font-weight: 400;
    margin: 0px 24px;
  }

  .history-list {
    margin-top: 24px;
    overflow-y: auto;
    gap: 1px;
    flex: 1;
    .history-item {
      cursor: pointer;
      position: relative;
      gap: 8px;
      justify-content: flex-start;
      align-items: flex-start;
      word-break: break-all;
      user-select: none;
      font-family: MiSans-Normal;
      font-size: 14px;
      color: #777e91;
      margin: 0 10px;
      padding: 14px 18px;
      --line-clamp: 2;
      text-overflow: ellipsis;

      .icon {
        width: 16px;
      }

      .ellipsis {
        line-height: 18px;
      }

      &:hover {
        // color: #3d4ac6;
        background: #fff;
        border-radius: 4px;
        .delete_btn {
          display: flex;
          width: auto;
        }
      }
      .delete_btn {
        width: 50px;
        height: 100%;
        background-image: linear-gradient(269deg, #ffffff 50%, rgba(255, 255, 255, 0) 100%);
        border-radius: 4px;
        position: absolute;
        right: 0;
        top: 0;
        display: none;
        align-items: center;
        justify-content: flex-end;
        padding-left: 20px;

        span {
          display: inline-flex;
          justify-content: center;
          align-items: center;
          width: 20px;
          height: 20px;
          margin-right: 8px;
          
          &:hover {
            background: #e1e5fa;
            border-radius: 4px;

            :deep(svg) {
              // margin: 0 12px 0 auto;
              width: 14px;
              height: 14px;

              path {
                fill: #3d4ac6;
              }
            }
          }
        }
      }
    }
    .history-item.active {
      // color: #3d4ac6;
      background: #fff;
      border-radius: 4px;
    }
    .no-data {
      height: 100%;
      font-family: MiSans-Normal;
      font-size: 12px;
      line-height: 16px;
      color: #a4a9b6;
      img {
        padding-right: 24px;
        margin-bottom: 30px;
      }
    }

    .no-data.loading::after {
      content: attr(data-loading);
    }
  }
    .clear-btn-border{
      height: 63px;
      padding: 10px 24px;
      position: absolute;
      left: 0;
      bottom: 0;
      width: 100%;
      background: #fff;

      .clear-btn {
        cursor: pointer;
        border: 1px solid #c1c1c1;
        border-radius: 4px;
        height: 43px;
        width: 100%;
        font-family: PingFangSC-Regular;
        font-size: 14px;
        color: #777e91;

      }


      :deep(.el-dropdown-link) {
        user-select: none;
      }
    }
}

.dropdown-menu {
  z-index: 1000 !important;
}


.menu-item-row {
  width: 100%;
  padding: 0;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;

  svg {
    margin-top: 5px;
    margin-right: 8px;
  }
}

</style>
<style lang="scss">


.playback-icon {
  margin: 0 3px;
  width: 20px;
  height: 20px;
  path {
    fill: #A4A9B6;
  }
}

.delete-tip {
  padding: 10px 16px;
  .el-popconfirm__main {
    white-space: nowrap;
    font-size: 14px;
    font-family: MiSans-Normal;
    color: #1c2848;
    max-width: 200px !important;
    white-space: pre-wrap !important;
  }
  .el-popconfirm__action {
    display: flex;
    button {
      width: 50%;
      --el-color-primary: #3d4ac6;
      --el-color-primary-light-3: #3d4ac6;
    }
    button:active {
      background: #313ca5;
    }
  }

  .el-message-box__close {
    color: #3d4ac6;
    &:hover {
      color: #3d4ac6;
    }
  }
  .el-message-box__btns {
    button {
      --el-color-primary: #3d4ac6;
      --el-color-primary-light-3: #3d4ac6;
    }
    button:active {
      background: #313ca5;
    }
  }
}


.el-dropdown__popper {
  margin-bottom: 15px;
  width: 212px !important;
}


@media screen and (max-height: 600px) {
  .no-data {
    display: none
  }
}
</style>
