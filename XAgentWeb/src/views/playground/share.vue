<template>
  <div class="main-page-container history-list">
    <div class="main-page-wrapper">
      <h3>Conversations Shared by Our Community</h3>

      <div>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          layout="total, ->, prev, pager, next"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :hide-on-single-page="true"
        />
      </div>

      <div class="conversations-list-wrapper" id="main-page-convs-list-wrapper">
        <div
          v-for="(item, index) in sharedTalksArr"
          :key="item.interaction_id"
          class="history-item conversations-list-item-card"
          :class="{ active: item.interaction_id === route.query.id }"
        >
          <!-- <img src="@/assets/images/playground/qp.svg" alt="" class="icon" draggable="false"/> -->
          <div class="header-info-row">
            <span class="order-info">
              {{ item.agent || "-" }} / {{ item.mode || "-" }}
            </span>
            <span class="setting-info"> </span>
          </div>

          <el-tooltip class="box-item" effect="dark" placement="top">
            <template #content>
              <div class="content-in-tooltip" slot="content">
                {{ item.parameters[0].goal }}
              </div>
            </template>
            <span class="ellipsis convs-title-name">
              {{ item.parameters[0].goal }}
            </span>
          </el-tooltip>

          <div class="footer-info-row">
            <span class="creator-info">
              by: {{ item.user_name || "Community User" }}
            </span>
          </div>

          <span class="delete_btn flex-row">
            <span
              class="playback-icon"
              title="Run the task"
              @click="runSharedItem(item, index)"
            >
              <VideoPlay />
            </span>
          </span>
        </div>
      </div>

      <div v-show="isContentLoading">
        <el-skeleton :loading="isContentLoading" animated style="width: 100%;" class="loading-skeleton-container">
            <template #template>
              <el-skeleton-item variant="rect" class="skeleton-item"/>
              <el-skeleton-item variant="rect" class="skeleton-item"/>
              <el-skeleton-item variant="rect" class="skeleton-item"/>
            </template>
        </el-skeleton>
      </div>
      
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();

const conversationsList = ref(
  new Array(10).fill(0).map((_, index) => {
    return {
      id: index,
      name: `name-${index}`,
      avatar: `avatar-${index}`,
      lastMessage: `lastMessage-${index}`,
      lastMessageTime: `lastMessageTime-${index}`,
      unreadCount: index,
    };
  })
);

const chatMsgInfoStore = useHistoryTalkStore();
const sharedTalksArr = computed(() => chatMsgInfoStore.getSharedArr);

const runSharedItem = (item: any, index: number) => {
  router.push({
    name: "viewTalk",
    params: {
      id: item.interaction_id,
      mode: "runshared",
    },
  });
};

const userStore = useUserStore();
const userInfo = userStore.getUserInfo;
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

const isContentLoading = ref(false);

const handleSizeChange = async (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
  await getSharedData();
};

const handleCurrentChange = async (val: number) => {
  currentPage.value = val;
  await getSharedData();
};

const getSharedData = async () => {

  if(sharedTalksArr.value.length > 0) {
    return;
  }

  // if(sessionStorage.getItem("sharedTalksLoaded") === "true") {
  //   return;
  // }

  // if(localStorage.getItem("sharedTalks")) {
  //   chatMsgInfoStore.setSharedArr(JSON.parse(localStorage.getItem("sharedTalks") || "[]"));
  //   return;
  // }

  isContentLoading.value = true;

  const res = await useSharedConvsRequest({
    user_id: userInfo?.user_id,
    token: userInfo?.token,
    page_size: pageSize.value,
    page_num: currentPage.value,
  });

  if (res?.success === true || res?.message === "success") {
    chatMsgInfoStore.setSharedArr(res?.data?.rows || []);
    total.value = res?.data?.total || 0;
    sessionStorage.setItem("sharedTalksLoaded", "true");
    
    if(res?.data?.rows ) {
      localStorage.setItem("sharedTalks", JSON.stringify(res?.data?.rows));
    } else {
      localStorage.setItem("sharedTalks", JSON.stringify([]));
    }

    isContentLoading.value = false;
  } else {
    ElMessage({ type: "error", message: res?.message || "Failed to get data" });
    isContentLoading.value = false;
  }
};

onMounted(() => {
  const getSharedTalks = async () => {
    await getSharedData();
  };
  getSharedTalks();
});
</script>

<style lang="scss" scoped>
$convs-list-item-width: 250px;

.main-page-container {
  padding: 20px calc(50vw - 130px - 32vw)  60px;
  height: 100%;
  background-color: rgb(236, 237, 245);

  h3 {
    font-size: 30px !important;
    line-height: 32px;
    margin: 0 0 20px 0;
  }

  .main-page-logo-header {
    padding: 0;
    height: auto;
    width: auto;
    max-width: 80vw;
    border: 1px solid red;
    background-color: blue;
    margin: 20px auto 0 auto;

    display: flex;
    flex-direction: column;
    align-items: center;

    .logo_name_border {
      margin: 40px 0px 32px 0px;
      align-items: center;
      .logo {
        height: 30px;
        width: 36px;
        margin-bottom: 16px;
      }
      .name {
        line-height: 16px;
        font-size: 16px;
      }
    }
    .new-talk {
      cursor: pointer;
      user-select: none;
      background: #3d4ac6;
      border-radius: 8px;
      font-family: MiSans-Regular;
      font-size: 15px;
      height: 40px;
      flex-basis: 40px;
      color: #ffffff;
      text-align: center;
      font-weight: 400;
      margin: 0px 24px;
      width: 200px;
    }
  }

  .conversations-list-wrapper {
    padding: 0;
    height: auto;
    width: 100%;
    max-width: 80vw;
    display: grid;
    grid-template-columns: repeat(
      auto-fill,
      minmax($convs-list-item-width, 1fr)
    );
    grid-gap: 20px;

    .conversations-list-item-card {
      padding: 0.8em !important;
      height: 120px;
      width: 100%;
      max-width: 80vw;
      margin: 20px auto 0 auto;
      box-shadow: 0 3px 6px 0 rgba(0, 0, 0, 0.25);
      transition: 0.3s;
      border-radius: 8px;
      align-items: flex-start;
      background-color: #f7f7fd;

      &:hover {
        box-shadow: 0 6px 12px 0 rgba(0, 0, 0, 0.25);
        scale: 1.01;
      }
    }
  }
}
.loading-skeleton-container {
  padding: 0;
  height: auto;
  width: 100%;
  max-width: 80vw;
  display: grid !important;
  grid-template-columns: repeat(
    auto-fill,
    minmax($convs-list-item-width, 1fr)
  );
  grid-gap: 20px;

    .skeleton-item {
      display: inline-block;
      padding: 0.8em !important;
      height: 120px;
      width: 100%;
      max-width: 80vw;
      margin: 20px auto 0 auto;
    }  
}


.history-list {
  overflow-y: auto;
  gap: 1px;
  flex: 1;
  .history-item {
    background-color: #fefefe;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: flex-start !important;
    justify-content: flex-start;
    word-break: break-all;
    user-select: none;
    font-family: MiSans-Normal;
    font-size: 16px;
    color: #494e5e;
    margin: 0 10px;
    padding: 16px 18px;
    position: relative;

    .header-info-row {
      width: 100%;
      height: 16px;
      display: flex;
      flex-direction: row;
      position: relative;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      .setting-info {
        bottom: 5px;
        right: 10px;
        font-family: MiSans-Normal;
        font-size: 12px;
        line-height: 16px;
        color: #a4a9b6;
      }
      .order-info {
        bottom: 5px;
        left: 10px;
        font-family: MiSans-Normal;
        font-size: 12px;
        line-height: 16px;
        color: #a4a9b6;
        border-radius: 50%;
        text-align: center;
      }
    }

    .footer-info-row {
      width: 100%;
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      position: absolute;
      bottom: 10px;
      left: 10px;

      .creator-info {
        bottom: 5px;
        left: 10px;
        font-family: MiSans-Normal;
        font-size: 12px;
        line-height: 16px;
        color: #a4a9b6;
      }
    }

    .icon {
      width: 16px;

      svg {
        width: 100%;
        height: 100%;
        path {
          fill: #3d4ac6 !important;
        }
      }
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
      width: auto;
      height: 100%;
      background-image: linear-gradient(
        269deg,
        #ffffff 50%,
        rgba(255, 255, 255, 0) 100%
      );
      border-radius: 4px;
      position: absolute;
      right: 0;
      bottom: 0;
      display: none;
      align-items: flex-end;
      justify-content: center;
      padding-bottom: 10px;

      span {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 25px;
        height: 25px;
        margin-right: 8px;

        &:hover {
          background: #e1e5fa;
          border-radius: 4px;

          :deep(svg) {
            // margin: 0 12px 0 auto;
            width: 20px;
            height: 20px;

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

.main-page-wrapper {
  border-radius: 8px;
  background-color: #fff;
  padding: 20px;
  width: 100%;
  // height: 100%;
}

.content-in-tooltip {
  width: 200px;
  height: auto;
  padding: 0;
  white-space: normal;
  word-break: break-all;
}
</style>
