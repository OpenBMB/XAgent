<template>
  <div
    class="content-title flex-row"
    v-show="subTasks.length !== 0 || isLatest"
  >
    <span> Outer Loop：</span>
  </div>
  <div
    v-if="subTasks.length === 0 && isLatest && pageMode !== 'review' && isLoading"
    class="loading-skeleton-wrapper"
  >
    <el-skeleton :rows="5" animated />
  </div>
  <div v-else-if="isLatest">
    <el-tabs
      type="border-card"
      class="tab-border"
      tab-position="left"
      :class="{ isZeroIndex: tabIndex === '0' }"
      @tab-change="tabChange"
      @tab-click="tabClick"
      v-model="tabIndex"
    >
      <el-tab-pane
        v-for="({ name, task_id, inner, goal }, index) in subTasks"
        :key="task_id"
        class="tab-pane"
      >
        <template #label>
          <span class="custom-tabs-label flex-row">
            <div className="iscomplete-icon-wrapper">
              <el-icon v-if="currentSubtaskIndex > index || isTaskCompleted"
                ><CircleCheck class="complete-icon"
              /></el-icon>
              <img
                v-if="currentSubtaskIndex === index && !isTaskCompleted"
                class="complete-icon spinning"
                src="@/assets/images/playground/tabLoading.svg"
              />
            </div>
            <span className="subtask-name">{{ name }}</span>
            <span>
              <el-button
                type="primary"
                plain
                color="#3D4AC6"
                v-if="
                  tabIndex === index + '' &&
                  currentSubtaskIndex === index &&
                  !isAutoMode
                "
                v-show="
                  !isSubtaskGenerating &&
                  currentInnerIndex === 0 &&
                  !isTaskCompleted
                "
                :disabled="!currentGoalStr"
                class="subtask-run-btn"
                @click="subtaskRun(index)"
              >
                <VideoPlay />
              </el-button>
            </span>
          </span>
          <el-input
            v-if="tabIndex === index + ''"
            :disabled="
              currentSubtaskIndex > index || currentInnerIndex > 0 || isAutoMode
            "
            class="inputbox-in-tab input-text"
            :autosize="{ minRows: 2, maxRows: 4 }"
            type="textarea"
            v-model="currentGoalStr"
          />
          <span v-else class="input-text">
            {{ subTasks[index] ? subTasks[index].goal : "" }}
          </span>

          <div class="bottom-shadow">
            <div class="circle1"></div>
            <div class="circle2"></div>
          </div>
        </template>
        <div class="flex-column subtask-top"></div>
        <div class="inner-title">
          👾 Inner Loop：<span class="inner-step">Subtask {{ index + 1 }}</span>
        </div>

        <!-- <div class="extend flex-row header-row" >
              <div class="extend-left flex-row">
                <span class="intro">🔧 Tool Recommendations：</span>
                <span class="sub-intro">success quote for ol...</span>
              </div>
              <img class="extendBtn" @click="changeShow" src="@/assets/images/playground/extend.svg" alt="show" />
            </div> -->

        <div
          class="subtask-tools-content"
          :class="{ subtaskToolsContentHide: !showTaskDetail }"
        >
          <div class="subtask-tools-content-top" v-show="false">
            <span class="subIntro" @click="collapseAll">Collapse All</span>
          </div>

          <el-collapse v-model="activeKeys">
            <TransitionGroup name="inner" tag="div">
              <el-collapse-item
                class="task-accordion"
                v-for="(item, innerIndex) in inner"
                :key="item.node_id"
                :name="innerIndex + ''"
              >
                <template #title>
                  <span class="box-subtask-title">
                    <b>🤖️ Step {{ innerIndex + 1 }} </b>
                  </span>
                </template>
                <Inferencing
                  @runComplete="runComplete"
                  @runToNext="runToNext"
                  :waitQueue="[]"
                  :tasksId="null"
                  :data="item"
                  :isLast="innerIndex === inner.length - 1"
                  :isEndNode="item.isEndNode ? true : false"
                  :currentInnerIndex="currentInnerIndex"
                  :currentSubtaskIndex="currentSubtaskIndex"
                  :subTaskNumber="index"
                  :innerNumber="innerIndex"
                  :isInRunningSubtask="index === currentSubtaskIndex"
                  :isInnerNodeGenerating="isInnerNodeGenerating"
                  :msgID="msgID"
                  :isFreezed = "subTasks[index].isShowRefinement === true"
                  :isAutoMode="isAutoMode"
                  :conversationId="conversationId"
                />
              </el-collapse-item>
              <div
                v-show="
                  ( 
                    subTasks[index].isShowRefinement === true || isTaskCompleted
                  ) && subTasks[index].refinement"
                class="task-refinement-wrapper"
                :key = "index + 'refinement'"
              >
                <TaskRefineInfo :data="subTasks[index].refinement" />
              </div>
            </TransitionGroup>
            <div
              v-if="currentSubtaskIndex === index && isLoading"
              v-show="isInnerNodeGenerating && !isTaskCompleted && !subTasks[index].isShowRefinement"
            >
              <el-skeleton :rows="3" animated />
            </div>
          </el-collapse>
        </div>
      </el-tab-pane>
    </el-tabs>  
  </div>
  <div v-if="subTasks.length === 0 && !isLatest" class="no-data-placeholder">
    No generated data.
  </div>
  <!-- 最新的正在加载中的那一条消息 -->
</template>

<script setup lang="ts">
import { ref } from "vue";
import Inferencing from "./Inferencing.vue";
import TaskRefineInfo from "./TaskRefineInfo.vue";
import { router } from "/@/router";

const route = useRoute();

const props = defineProps([
  "msgID",
  "conversationId",
  "complete",
  "mode",
  "isLatest",
  "pageMode",
  "isLoading",
]);

const emit = defineEmits(["runSubtask", "runInner", "disconnect"]);

const taskStore = useTaskStore();
const taskInfo = storeToRefs(taskStore);
const { subtasks: subTasks } = storeToRefs(taskStore);

const isOnlyExpandLastInner = ref(false);

const isLatest = computed(() => {
  return props.isLatest;
}); // 此时是不是消息列表里最新发生的那一条

const pageMode = computed(() => {
  return props.pageMode;
}); //

const { isAutoMode: isAutoMode } = storeToRefs(taskStore);

const getCollapseTitle = (index: number, item: any) => {
  const _is_end_node = item.isEndNode ? true : false;
  if (_is_end_node) {
    return "Submit Subtask Using Tools";
  } else {
    return `🤖️ Step ${index + 1}:   ${item.thoughts.substr(0, 30)}...`;
  }
};

const chatMsgInfoStore = useHistoryTalkStore();
const waitQueue = ref([] as Array<string>);
const conversationIdN = ref((route.query.id as string) || "config");
const tabIndex = ref("0" as string);

const setting = chatMsgInfoStore.getSetting(conversationIdN.value);

const isSubtaskGenerating = ref(false);
const isInnerNodeGenerating = ref(true);
const isInnerNodeEditabled = ref(props?.mode === "auto" ? false : true);
const isLoading = computed(() => props.isLoading);

const { isCompleted: isTaskCompleted } = storeToRefs(taskStore);

const {
  current_subtask_index: currentSubtaskIndex,
  current_inner_index: currentInnerIndex,
} = storeToRefs(taskStore);

const currentGoalStr = computed({
  get: () => {
    return (
        taskInfo.subtasks.value[parseInt(tabIndex.value)] ? taskInfo.subtasks.value[parseInt(tabIndex.value)].goal : ""
    );
  },
  set: (val) => {
    taskStore.setStepGoal(parseInt(tabIndex.value), val);
  },
});

const activeKeys = ref([] as Array<string>);
const showTaskDetail = ref(true);


watch(currentInnerIndex, (val) => {
  if(taskInfo.subtasks.value.length === 0) {
    return;
  }
  const _sub_task = taskInfo.subtasks.value[parseInt(tabIndex.value)];
  if(!_sub_task) {
    return;
  }
  const inners = _sub_task.inner;
  const len = inners.length;
  if (isOnlyExpandLastInner.value) {
    if (inners && len < 2) {
      activeKeys.value = inners.map((item: any, index: number) => (index + ""));
    
    } else {
      activeKeys.value = [len - 1 + ""];
      // if(tabIndex.value === currentSubtaskIndex + "") {
      //   activeKeys.value = [len - 1 + ""];
      // } 
      // only  set on current active tab
    }
    // set the last one as  active
  } else {
    if (val === 0) {
      activeKeys.value = [];
    } else {
      const _ = val - 1;
      activeKeys.value.push(_.toString());
    }
  }
});

watch(currentSubtaskIndex, (newVal, oldVal) => {
  // if(tabIndex.value !== oldVal + "") {

  // } // 
  tabIndex.value = newVal + "";
});

const insertQueue = () => {
  // const queue = [] as Array<string>
  // props.subtasks[props.subtasks.length - 1].tools.forEach((cmp: any) => {
  //   queue.push(cmp.id)
  // })
  // waitQueue.value = queue
};
// watch(props.subTasks, ()=>{
//   debugger
// })
let insertQueueOnce = () => {
  insertQueue();
  insertQueueOnce = () => {};
};
watchEffect(() => {
  if (props.mode === "auto") {
    if (props.complete) {
      insertQueueOnce();
      return;
    }
    // if(props.subtasks) {
    //   // 执行队列操作
    //   insertQueue()
    // }
  }
});

onBeforeMount(() => {
  if (props.mode === "auto") {
    if (!props.complete) {
      insertQueue();
    }
  }
});

// 执行queue的anshift操作
const runComplete = () => {
  waitQueue.value.shift();
};
const tabChange = (val: string) => {
  tabIndex.value = val;
};

const changeShow = () => {
  showTaskDetail.value = !showTaskDetail.value;
};

const tabClick = (val: string) => {};

const subtaskRun = (_index: number) => {
  const querystr = subTasks.value[_index].goal;
  emit("runSubtask", querystr);
  isSubtaskGenerating.value = true; 
  if (currentInnerIndex.value === 0 || props.mode === "auto") {
    isInnerNodeGenerating.value = true;
  }
};

const runToNext = (_i: any) => {
  const _inner_index = _i.innerNumber;
  const _subtask_index = _i.subTaskNumber;
  const query = subTasks.value[_subtask_index].inner[_inner_index]

  emit("runInner", {
    thoughts: query.thoughts,
    reasoning: query.reasoning,
    plan: query.plan,
    criticism: query.criticism,
  });
  
  isInnerNodeGenerating.value = true;
};

const gotNewInnerNode = () => {
  isSubtaskGenerating.value = false;
  if (props.mode === "manual") {
    isInnerNodeGenerating.value = false;
  }
};

const jumpToNextSubtask = () => {
  isSubtaskGenerating.value = false;
  if (props.mode === "manual") {
    isInnerNodeGenerating.value = false;
  }
};

const isAllCollapsed = ref(false);

const collapseAll = () => {
  activeKeys.value = [];
  isAllCollapsed.value = true;
};

const expandAll = () => {
  activeKeys.value = subTasks.value[parseInt(tabIndex.value)].inner.map(
    (item: any, index: number) => {
      return index + "";
    }
  );
};

const setTaskComplete = () => {
  isTaskCompleted.value = true;
  isInnerNodeGenerating.value = false;
  isSubtaskGenerating.value = false;
};

defineExpose({
  gotNewInnerNode,
  jumpToNextSubtask,
  setTaskComplete,
});
</script>

<style scoped lang="scss">
@import url(../../../assets/css/animation.css);

.el-tabs {
  :deep(.el-tabs__content) {
    min-height: 400px;
  }
}

.box-subtask-title {
  display: inline-block;
  white-space: nowrap; 
  width: 100%; 
  overflow: hidden;
  text-overflow:ellipsis;
  line-clamp: 1;
  -webkit-line-clamp: 1;
  margin-left: -10px;
  padding-left: 5px;
  max-width: calc(64vw - 400px);
  text-align: left
}

.bottom-shadow {
  display: none;
}
.tab-border {
  background-color: unset;
  border: 0;
  width: 100% !important;

  .subtask-name {
    height: auto;
    line-clamp: 1;
    display: block;
    overflow: hidden;
    width: auto;
    max-width: 170px;
    white-space: pre-wrap;
    text-align: left;
    text-overflow: ellipsis;
  }

  .custom-tabs-label {
    align-items: center;
    column-gap: 4px;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: flex-start;

    .iscomplete-icon-wrapper {
      height: 30px;
      width: 15px;
      padding: 0;
      padding-top: 3px;
      text-align: left;

      .complete-icon {
        height: 14px;
        width: 14px;
        color: #0a9d00;
        margin: 0;
      }

      .spinning {
        animation: linear rotate_animate 1.5s infinite;
      }
    }
  }

  .header-row {
    width: 100%;
    height: 50px;
    line-height: 50px;
    padding: 12px 20px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
  }

  .extend {
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    padding: 12px 20px;
    margin-top: 10px;
    margin-bottom: 12px;
    .icon {
      height: 20px;
      width: 20px;
      background-color: #676c90;
    }
    .intro {
      font-family: PingFangSC-Medium;
      font-size: 14px;
      color: #1c2848;
      letter-spacing: 0;
      line-height: 26px;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-clamp: 1;
      height: 26px;
    }
    .sub-intro {
      color: #676c90;
      font-family: PingFangSC-Medium;
      letter-spacing: 0;
      font-size: 14px;
      line-height: 26px;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-clamp: 1;
      height: 26px;
    }
    .extendBtn {
      height: 15px;
      width: 15px;
      cursor: pointer;
    }
  }

  .inner-title {
    font-family: PingFangSC-Medium;
    font-size: 14px;
    color: #1c2848;
    letter-spacing: 0;
    line-height: 26px;
    font-weight: 500;
    margin-bottom: 10px !important;

    .inner-step {
      color: #676c90;
      font-family: "PingFangSC-Regular";
      font-weight: 400;
    }
  }
  .subtask-tools-content {
    .subtask-tools-content-top {
      font-size: 14px;
      letter-spacing: 0;
      line-height: 26px;
      margin-bottom: 8px;
      .intro {
        font-family: PingFangSC-Medium;
        color: #1c2848;
        font-weight: 500;
        padding-left: 10px;
      }
      .subIntro {
        font-family: PingFangSC-Regular;
        color: #676c90;
        font-weight: 400;
        cursor: pointer;
      }
    }
    :deep(.el-collapse) {
      border: none !important;

      .el-collapse-item {
        margin-bottom: 10px;
        border-radius: 8px;
        overflow: hidden;
        position: relative;
      }

      .el-collapse-item__content {
        border-radius: 0 0 8px 8px !important;
        padding-bottom: 0px !important;
        overflow: hidden !important;
      }
      .el-collapse-item__header {
        padding-left: 20px;
        font-family: PingFangSC-Medium;
        font-size: 14px;
        color: #1c2848;
        letter-spacing: 0;
        line-height: 48px;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        line-clamp: 1;
        height: 48px;
        background-color: #fff;
        user-select: none;
      }
      .is-active {
        .el-collapse-item__wrap {
          border-radius: 0px;
        }
      }
    }
  }
  // 组建样式修改
  :deep(.el-tabs--border-card) {
    background-color: unset;
    border: 0;
  }
  :deep(.el-tabs__header) {
    background-color: transparent !important;
    border-color: transparent !important;
    box-shadow: none !important;
    margin-right: -1px !important;
  }
  :deep(.el-tabs__content) {
    background-color: rgb(245, 246, 249);
    border-radius: 8px;
  }
  :deep(.el-tabs__nav) {
    padding-bottom: 10px;
    gap: 10px;
    .el-tabs__item {
      height: auto;
      width: 240px;
      border-radius: 8px;
      border: 0;
      position: relative;
      transition: 0s;
      font-family: "PingFangSC-Medium";
      font-size: 14px;
      color: #1c2848;
      letter-spacing: 0;
      line-height: 26px;
      font-weight: 500;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
      padding: 12px 20px 15px 20px !important;

      textarea {
        width: 100%;
        max-width: 262px;
        resize: none;
        border: none;
        background: transparent;
        border-color: transparent;
        -ms-overflow-style: none; /* IE and Edge */
        scrollbar-width: none; /* Firefox */

        &::-webkit-scrollbar {
          display: none;
        }
      }
    }
    .is-active {
      background-color: rgb(245, 246, 249);
      color: aliceblue;
      font-family: "PingFangSC-Medium";
      font-size: 14px;
      color: #1c2848;
      letter-spacing: 0;
      line-height: 26px;
      font-weight: 500;
      border-radius: 8px 0 0 8px;
      width: auto;

      textarea {
        width: 100%;
        max-width: 262px;
        resize: none;
        background: #ffffff;
        border-color: #dcdcdc;
        border-radius: 8px;
        font-family: "PingFangSC-Regular";
        font-size: 14px;
        color: rgba(0, 0, 0, 0.9);
        letter-spacing: 0;
        line-height: 22px;
        font-weight: 400;
      }

      .bottom-shadow {
        position: relative;
        background-color: rgb(23, 71, 215);
        overflow: hidden;
        z-index: 10;

        .circle1 {
          position: absolute;
          height: 20px;
          width: 20px;
          left: -10px;
          top: -11px;
          background-color: rgb(236, 237, 245);
          border-radius: 50%;
        }
        .circle2 {
          position: absolute;
          height: 20px;
          width: 20px;
          right: -10px;
          top: -11px;
          background-color: rgb(236, 237, 245);
          border-radius: 50%;
        }
      }
    }
  }
}
.isZeroIndex {
  :deep(.el-tabs__content) {
    border-top-left-radius: 0;
  }
}
.subtaskToolsContentHide {
  height: 0px;
  overflow: hidden;
}

.input-text {
  font-family: "PingFangSC-Regular";
  font-size: 14px;
  color: #676c90;
  letter-spacing: 0;
  line-height: 26px;
  font-weight: 400;
  max-width: 215px;
  white-space: pre-wrap;
  text-align: left;
  text-overflow: ellipsis;
  line-clamp: 2;
}

.subtask-run-btn {
  background: transparent !important;
  font-family: "PingFangSC-Medium";
  font-size: 12px;
  letter-spacing: 0;
  line-height: 18px;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  margin-left: 10px;
  position: absolute;
  right: 5px;
  top: 10px;
  height: 24px;
  text-align: center;
  width: auto;
  height: auto;
  border-radius: 50%;
  border: none !important;

  span {
    background-color: #fff;

    svg {
      color: #3d4ac6;
      line-height: 24px;
      height: 18px !important;
      width: 18px !important;
    }
  }
}

.content-title {
  font-family: PingFangSC-Medium;
  font-size: 14px;
  color: #1c2848;
  letter-spacing: 0;
  line-height: 26px;
  margin-bottom: 12px;

  span {
    font-weight: 700 !important;
  }
}

.no-data-placeholder {
  width: 100%;
  border-radius: 8px;
  padding: 12px 20px;
  background: rgba(240, 240, 240, 0.9);
  font-family: "PingFangSC-Medium";
  font-size: 14px;
  color: #1c2848;
}

.inner-enter-active,
.inner-leave-active {
  transition: all 0.5s ease;
}
.inner-enter-from,
.inner-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.loading-skeleton-wrapper {
  background: rgba(255, 255, 255, 0.4);
  padding: 20px;
  border-radius: 8px;
  border: none;
}

:deep(.el-tabs__item.is-active) {
  background-color: #f5f6f9 !important;
  border-color: #f5f6f9 !important;
  box-shadow: none !important;
}
</style>
<!-- <style lang="scss">

</style> -->
