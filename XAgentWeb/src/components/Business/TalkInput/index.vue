<template>
  <div class="talk-input-border flex-row">
    <div
      class="talk-input flex-column"
      :class="{ sensitive: isSensitive, focus: isFocus }"
      :style="{ '--line-length': input.split('\n')?.length }"
    >
      <el-input
        ref="inputRef"
        v-model="input"
        type="textarea"
        rows="1"
        placeholder="Please enter your question"
        maxlength="2000"
        contenteditable
        :autofocus="isFocus"
        @focus="isFocus = true"
        @blur="isFocus = false"
        @keydown.enter="enterInput"
      />
    </div>
      <el-button 
        type="primary"
        color="#3D4AC6"
        class="send-btn submit"
        :disabled = "isProgress || input.length <= 0"
        @click="sendMessage"
      >
        <img 
          alt="" 
          v-show="!isProgress"
          src="@/assets/images/playground/send.svg" 
        />
        <LoadingDot v-show="isProgress" />
      </el-button>
  </div>
  

    <!-- <div class="operate flex-row flex-center">
      <span class="length">{{ input.replace(/\n/g, '').length }} / 2000 </span>

      <span class="tip">Shift+Enter键换行</span>
      <div class="btn flex-row flex-center" :class="{ disabled: input.length <= 0 }">
        <img src="@/assets/images/playground/clear.svg" alt="" @click="clearMessage" />
        <img v-show="!isProgress" src="@/assets/images/playground/send.svg" alt="" @click="sendMessage" />

        <LoadingDot v-show="isProgress" />
      </div>
    </div> -->

    <!-- <div class="word-sensitive-wrapper">
      <div class="word-sensitive flex-row flex-center">
        <img src="@/assets/images/playground/warning.svg" />
        <span>根据相关安全规定，您的内容无法显示。</span>
      </div>
    </div> -->
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';

// TODO: 最多下发10轮对话
const emits = defineEmits<{ (e: 'sendMessage', data: string): void }>()
const props = withDefaults(defineProps<{ message?: string; isProgress?: boolean }>(), { message: '', isProgress: false })
const { message: outInput, isProgress } = toRefs(props)

const route = useRoute()

const isSensitive = ref(false)
const isFocus = ref(false)
const inputRef = ref<Nullable<HTMLInputElement>>()
const input = ref('')

watchEffect(() => {
  input.value = outInput.value
  if (route.query) {
    inputRef.value?.focus()
  }
})

const historyTalkStore = useHistoryTalkStore()
const { isRequestingAi } = storeToRefs(historyTalkStore)

const enterInput = (e: any) => {
  if (e.shiftKey && e.keyCode === 13) {
    e.stopPropagation()
    e.preventDefault()

    const startPos = e.target.selectionStart
    const endPos = e.target.selectionEnd
    input.value = input.value.substring(0, startPos) + '\n' + input.value.substring(endPos)

    setTimeout(() => {
      e.target.setSelectionRange(startPos + 1, startPos + 1)
    })

    setTimeout(() => {
      const textarea = document.querySelector('.el-textarea__inner') as HTMLElement
      textarea.scrollTop = textarea.scrollHeight
    })
    return
  }

  if (!e.shiftKey && e.keyCode === 13) {
    e.preventDefault()
    const val = input.value.replace(/\n/g, '')
    if (val.length > 0) {
      sendMessage(e)
    }
  }
}

const sendMessage = async ($event: any, val?: string) => {
  if (!(await useCheckAuth())) return
  if (isProgress.value) return
  if (isRequestingAi.value) {
    ElMessage({ 
        type: 'warning',
        message: `You have a request in progress, 
          please wait for the request to complete and try again.`
    });
    return
  }
  const value = val || input.value
  // if (useIsExistSensitive(value)) {
  //   isSensitive.value = true

  //   setTimeout(() => {
  //     isSensitive.value = false
  //     input.value = ''
  //   }, 3000)

  //   return
  // }

  emits('sendMessage', unref(input))
  nextTick(() => (input.value = ''))
}

const clearMessage = () => {
  input.value = ''
}
</script>

<style scoped lang="scss">
.talk-input-border{
  column-gap: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  .gradient-mask {
    width: 100%;
    height: 64px;
    position: absolute;
    left: 0;
    top: 0;
    transform: translateY(-100%);
    background: linear-gradient(180deg, rgba(235,236,248,0.00) 0%, #EAEBF9 100%);
    z-index: 40;
}
  
}
.talk-input {
  flex: 1;
  // min-height: 88px;
  max-height: 350px;
  margin: 0 var(--size-50100);

  position: sticky;
  bottom: 0;
  z-index: 110;

  background-color: #fff;
  border: 1px solid #eee;
  border-radius: 8px;

  :deep(.el-textarea) {
    flex: 1;
    height: 100%;
    border: 0;
    background: transparent;
    .el-textarea__inner {
      max-height: 200px;
      height: calc(calc(var(--line-length) + 1) * 14px);
      padding: 10px 12px;
      box-shadow: none;
      font-family: PingFangSC-Regular;
      font-size: 14px;
      line-height: 14px;
      border-radius: 8px;
      resize: none;
    }
    textarea{
      min-height: 34px !important;
      &::placeholder{
        color: #eee;
        font-family: PingFangSC-Regular;
        font-size: 14px;
        color: #CCCCCC;
        font-weight: 400;
      }
    }
  }

  .operate {
    min-height: 28px;
    width: 100%;
    font-family: PingFangSC-Regular;
    font-size: 12px;
    color: #cccccc;
    font-weight: 400;
    padding: 0 24px 12px;
    border-radius: 0 0 8px 8px;
    background: #fff;

    .length {
      user-select: none;
    }

    .tip {
      margin-left: auto;
      margin-right: 24px;
      user-select: none;
    }
    .btn {
      gap: 16px;
      img {
        cursor: pointer;
        width: 16px;
        height: 16px;
      }

      &.disabled {
        cursor: default;
        :deep(svg) {
          path {
            fill: #ccc;
          }
        }
      }
    }
  }

  &.focus {
    border-color: #3d4ac6;
  }

  &.sensitive .word-sensitive-wrapper {
    animation: fadeInBottom 0.6s ease-in-out forwards;
  }

  .word-sensitive-wrapper {
    pointer-events: none;
    position: absolute;
    bottom: 120%;
    z-index: 10;
    // transform: translateY(30px);
    opacity: 0;
    width: 100%;
    display: flex;
    justify-content: center;

    .word-sensitive {
      width: fit-content;
      padding-bottom: 0;
      background: #fffdfc;
      border: 1px solid #ffd1ba;
      border-radius: 4px;

      font-family: PingFangSC-Regular;
      font-size: 12px;
      color: #1c2848;
      letter-spacing: 0;
      font-weight: 400;
      display: flex;
      flex-direction: row;
      gap: 10px;

      padding: 10px 20px;
    }
  }
}
.submit{
  flex-basis: 86px;
  height: 34px;
  width: 86px;
  background: #3D4AC6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  img{
    height: 16px;
    width: 16px;
    background: transparent;
    transform: rotate(-35deg);
    margin-bottom: 5px;
  }
}

.send-btn {
  width: 86px;
  height: 34px;
  padding: 5px !important;
  background: #3D4AC6;
  border-radius: 8px;

  path {
    scale: 1.33 !important;
  }
}
</style>
