<template>
    <div class="infer-border flex-column">
      <div v-if="!isEndNode">
          <div
            class="flex-row row" v-for="(keyName, index) in dataObjKeys"
            :key="keyName">
              <span class="key-name-label">{{ keyName }}:</span>
              
              <div class="read-only-input" 
                  v-if="data.complete">
                <span>
                  {{ dataObj[keyName]}}
                </span>
              </div>

              <el-input
                  v-else
                  type="textarea"
                  :autosize="{ minRows: 1, maxRows: 10}"
                  class="input"
                  :disabled="isAutoMode"
                  v-model="dataObj[keyName]"
                >
                <template #suffix>
                  <img @click="resetInput(keyName)" class="reset-icon"
                    src="@/assets/images/playground/icon_reset.svg" />
                </template>
              </el-input>

          </div>
      </div>
      <div class="subtask-submit-info" >
        <div class="end-subtask-info-title" v-show="!isEndNode" >
          <span>using Tools:</span>
        </div>
        <SubmitSubtaskInfo :data="dataObj.using_tools" />
      </div>
      <!-- <el-row
        :gutter="0"
        v-show="data.complete"
        class="detail-row flex-row">
        <div class="detail-row-left">
          <img /> <span>🔧 using Tools:</span><span>success quote for olato quotes</span>
        </div>
        <img src="@/assets/images/playground/eyes.svg" alt="showDetail" class="showMoreIcon" @click="showModal" />
      </el-row> -->

      <el-row
        :gutter="0"
        v-if="false"
        class="detail-row flex-row">
        <div class="detail-row-left">
          <img />
          <span>🔧 Using Tools:</span>
          <span>success quote for olato quotes</span>
        </div>
        <img src="@/assets/images/playground/eyes.svg" alt="showDetail" class="showMoreIcon"/>
      </el-row>

      <el-row :gutter="0" justify="end" v-show="!isFreezed">
        <el-button 
          type="primary"
          plain
          v-show="isLast && isInRunningSubtask && !isTaskCompleted"
          :loading="isInnerNodeGenerating"
          color="#3D4AC6"
          class="run-btn flex-row flex-center" 
          :class="{ disable: data.complete || data.unClickbel}"
          @click="runToNextNode(data.complete || data.unClickbel)"
          >RUN</el-button>
        <!-- <img v-if="runLoading" src="@/assets/images/playground/refreshNew.svg"/> -->
        <!-- <el-button plain type="primary" @click="runActive(data.complete || data.unClickbel)" :loading="runLoading" :disabled="data.complete || data.unClickbel">RUN</el-button> -->
      </el-row>

    </div>


    <el-dialog
      v-model="dialogVisible"
      title="Tips"
      width="30%"
      :before-close="handleClose"
    >
      <ModalInfo :list="list" />
    </el-dialog>
</template>
  
<script setup lang="ts">
  import { ref } from 'vue'
  import ModalInfo from './ModalInfo.vue'
  import { ElMessage } from 'element-plus'
  import  SubmitSubtaskInfo  from "./SubmitSubtaskInfo.vue"
  const chatMsgInfoStore = useHistoryTalkStore()
  
  const props = defineProps([
      'data', 'isLast', 
      'conversationId', 'msgID',
      'tasksId', 'waitQueue',
      "isEndNode", // 是不是当前某个subtask最后一个inner
      'isInRunningSubtask', 'isAutoMode',
      'currentInnerIndex', 'currentSubtaskIndex',
      "isInnerNodeGenerating",
      "subTaskNumber", "innerNumber", "isFreezed"
  ]);


  const isEndNode = computed(() => props.isEndNode as boolean);
  const isFreezed =  computed(() => props.isFreezed as boolean);
  const subTaskNumber = computed(() => props.subTaskNumber)
  const innerNumber = computed(() => props.innerNumber)

  const emit = defineEmits(['runComplete', 'runToNext']);

  const dataItem = {
    ...toRaw(props.data)
  };
  
  const dataObj = computed({
    get: () => {
      return taskInfo.subtasks.value[subTaskNumber.value].inner[innerNumber.value]
    },
    set: (val) => {
      taskStore.setInnerItem(val, subTaskNumber.value, innerNumber.value)
    }
  });

  const dataObjKeys = [
    'thoughts', 'reasoning', 'plan', 'criticism'
  ]

  const isLast = computed(() => props.isLast);

  const taskStore = useTaskStore();
  const taskInfo = storeToRefs(taskStore);

  const {
    isCompleted: isTaskCompleted
  } = storeToRefs(taskStore);

  const isAutoMode = computed(() => props.isAutoMode) // 是否是自动模式
  
  const currentInnerIndex = computed(() => props.currentInnerIndex) // 当前内部索引
  const currentSubtaskIndex = computed(() => props.currentSubtaskIndex) // 当前子任务索引
  const isInRunningSubtask = computed(() => props.isInRunningSubtask)

  const isInnerNodeGenerating = computed(() => props.isInnerNodeGenerating)

  const thought = ref(props.data.thought || "thought") // 字段值
  const apiName = ref(props.data.apiName || "apiName") // 字段值  "apiName
  const apiParameter = ref(props.data.apiParameter || "apiParameter") // 字段值
  const list = ref([]) // 弹层详细信息列表
  const runLoading = ref(false) // 执行run操作 按钮loading状态存值
  const dialogVisible = ref(false)

  const resetInput = (name: string) => {
    dataObj.value[name] = dataItem[name]
  }

  const runToNextNode = async(bool: boolean) => {
    if(bool) return

    runLoading.value = true
    // const result = await runRequest({
    //   thought: thought.value,
    //   apiName: apiName.value,
    //   apiParameter: apiParameter.value,
    //   id: props.data.id,
    // })
    // 此API在正式环境不可用
    // return
    // data: {
    //     list: [],
    // },
    // code: 0,
    // message: 'Success'

    const param = toRaw(dataItem)

    emit('runToNext', {
      subTaskNumber: subTaskNumber.value,
      innerNumber: innerNumber.value,
    });

    runLoading.value = false
    
    // if(result.data.code === 0) {
    //   if(props.isLast) {
    //     // 如果是最后一个元素 则将新的task插入到当前会话里面  判断数据返回  如果没有新的task 则止步于此
    //     // 最后一个步骤

    //     const data = chatMsgInfoStore.getCurrentMessage(props.conversationId, props.msgID)
    //     // 如果任务完成  则再发送请求 跳到下一个subtask
    //     if(data.complete) {
    //       // 如果整个任务完成，他就是最后一个subtask 无需请求下一个。
    //       chatMsgInfoStore.updateInferencing(props.conversationId, props.msgID, props.tasksId, props.data.id, true)
    //       return
    //     }
    //     const {data: res} = await getNewTaskData({})
        
    //     // 此API在正式环境不可用

    //     // return newTaskData


    //     const copy = {...res}
    //     copy.data.data.tasksId = new Date().getTime() + '' //测试代码  生成不同id
    //     // 测试代码  生成不同toolId 便于辨识当前执行run
    //     copy.data.data.tools = copy.data.data.tools.map((cmp: any, index: number) => {
    //       return {...cmp, ...{id: new Date().getTime() + index + ''}}
    //     })
    //     if(copy.data.isAll) {
    //       chatMsgInfoStore.requestComplete(props.conversationId, props.msgID, props.tasksId, props.data.id)
    //     }
    //     chatMsgInfoStore.addSubTask(props.conversationId, props.msgID , props.tasksId, props.data.id, copy.data.data)
    //     emit('runComplete', {})
    //     // 执行回调
    //   } else {
    //     chatMsgInfoStore.updateInferencing(props.conversationId, props.msgID, props.tasksId, props.data.id, false)
    //     emit('runComplete', {})
    //   }
    // }
    
  }
  watchEffect(()=>{
    if(props.data.id === props.waitQueue[0]){
      // 判断是否执行到自身
      // 执行run操作  然后执行回调
      
      // runActive(false)
    }
  })

  const handleClose = (done: () => void) => {
    done()
  }
</script>

<style scoped lang="scss">
  @import url(../../../assets/css/animation.css);
  .run-btn{
    width: 76px;
    height: 34px;
    border-radius: 8px;
    font-family: PingFangSC-Medium;
    font-size: 14px;
    letter-spacing: 0;
    line-height: 26px;
    font-weight: 500;

    cursor: pointer;
    img{
      height: 13px;
      width: 13px;
      animation: linear rotate_animate 1.5s infinite;
    }
  }
  .disable{
    opacity: 0.5;
    cursor: not-allowed;
  }
  .detail-row{
    align-items: center;
    justify-content: space-between;
  }
  .showMoreIcon{
    height: 20px;
    width: 20px;
    cursor: pointer;
  }
  .infer-border{
    width: 100%;
    padding: 10px;
    row-gap: 10px;
  }
  .row{

    align-items: center;
    margin: 0 5px  10px  5px;
    display: flex;
    flex-direction: column;

    .key-name-label{
      width: 100%;
      height: auto;
      padding-right: 16px;
      text-align: left;
      font-family: PingFangSC-Regular;
      font-size: 14px;
      color: #000000;
      letter-spacing: 0;
      line-height: 22px;
      font-weight: 600;
    }

    .read-only-input{
      flex: 1;
      width: 100%;
      span{
        font-family: 'PingFangSC-Regular';
        font-size: 14px;
        color: #676C90;
        letter-spacing: 0;
        line-height: 26px;
        font-weight: 400;
      }
    }
    .input{
      flex: 1;
      width: 100%;

      textarea{
        width: 100%;
        height: auto;
      }

      :global(.el-input__wrapper) {
        border-radius: 8px;
      }
      :global(.el-input-group__append){
        background-color: unset;
        border: 0px;
        padding: 0 10px;
        cursor: pointer;
      }

      img {
        cursor: pointer;
      }
    }
  }

  .end-subtask-info-title {
        width: 100%;
        height: auto;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: flex-start;
        font-family: PingFangSC-Medium;
        font-size: 14px;
        color: #1C2848;
        letter-spacing: 0;
        line-height: 26px;
        margin-top: -10px;

        span {
          font-weight: 700 !important;
        }
    }

    :deep(.jv-item.jv-string) {
        color: #676C90 !important;
    }  
</style>
    