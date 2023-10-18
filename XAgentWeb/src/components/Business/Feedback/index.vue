<template>
  <section class="feedback flex-row flex-center">
    <i class="copy-icon flex-row flex-center" title="复制" @click="copy"><IconCopy /></i>
    <i class="flex-row flex-center" title="赞" :class="{ active: data.rating === 'THUMBS_UP' }" @click="evaluate('THUMBS_UP')">
      <IconGood />
    </i>
    <el-popover
      ref="feedbackRef"
      placement="bottom-end"
      trigger="click"
      popper-class="bad-tip-popover"
      width="100%"
      @blur="isShowFeedback = false"
    >
      <template #reference>
        <i
          class="flex-row flex-center"
          title="踩"
          :class="{ active: data.rating === 'THUMBS_NO' && data.feedbackMsg }"
          @click="isShowFeedback = !isShowFeedback"
        >
          <IconBad />
        </i>
      </template>

      <div class="bad-tip flex-column">
        <div class="title flex-row">
          <span>💡您的反馈将帮助X-Agent优化进步</span>
        </div>
        <div v-for="({ title, tip }, index) in tipList" :key="index">
          <div class="tip-item-title">{{ title }}</div>
          <div class="tip-item flex-row">
            <span
              v-for="(item, idx) in tip"
              :key="idx"
              class="content"
              :class="{ active: feedbackForm.activeOptions.includes(item) }"
              @click="changeTag(item)"
            >
              {{ item }}
            </span>
          </div>
        </div>

        <div class="other-input flex-row">
          <el-input v-model="feedbackForm.text" placeholder="其他问题" />
          <button class="button" @click="submitFeedback">提交反馈</button>
        </div>
      </div>
    </el-popover>
  </section>
</template>

<script setup lang="ts">
import ClipboardJS from 'clipboard'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { feedbackRating } from '/#/talk-type'

const emits = defineEmits<{ (e: 'evaluateSuccess', data: { rating: feedbackRating; feedbackMsg: string; messageId: string }): void }>()

const props = withDefaults(
  defineProps<{
    data: {
      content: string
      msgID: string
      role: 'AI' | 'USER'
      conversationId: string
      feedbackMsg: string
      rating: string
    }
  }>(),
  {}
)
const { data } = toRefs(props)

const feedbackRef = ref()
const isShowFeedback = ref(false)
const feedbackForm = reactive<{ text: string; activeOptions: string[] }>({ text: '', activeOptions: [] })

watchEffect(() => {
  if (data.value.feedbackMsg) {
    const msgSplit = data.value.feedbackMsg.split(';')
    feedbackForm.text = msgSplit[1]
    feedbackForm.activeOptions = msgSplit[0].split('|')
  } else {
    feedbackForm.text = ''
    feedbackForm.activeOptions = []
  }
})

const tipList = reactive([
  {
    title: '题目理解问题',
    tip: ['文不对题', '提出的要求未完全覆盖', '无法根据指令调整', '上下文理解有误', '存在其他不符合预期的情况'],
  },
  {
    title: '回复问题',
    tip: ['存在事实性问题', '存在逻辑推理问题', '多条回复相似重复', '回复不够简练或核心点不突出', '排版问题', '内容不够专业'],
  },
  { title: '公序良俗问题', tip: ['存在违法信息', '存在偏见和歧视内容', '其他价值观问题'] },
])

const changeTag = (id: string) => {
  if (feedbackForm.activeOptions.includes(id)) {
    feedbackForm.activeOptions = feedbackForm.activeOptions.filter((item) => item !== id)
  } else {
    feedbackForm.activeOptions.push(id)
  }
}

const submitFeedback = () => {
  if (feedbackForm.activeOptions[0] || feedbackForm.text) {
    evaluate('THUMBS_NO', `${feedbackForm.activeOptions.join('|')};${feedbackForm.text}`)
  } else {
    ElMessage({ type: 'warning', 
    message: 'Please select or enter your feedback'
  })
  }
}

const route = useRoute()
const evaluate = async (rating: feedbackRating, text: string = '') => {
  const res = await useFeedbackRequest({
    messageId: data.value.msgID,
    feedbackMsg: text,
    rating,
    conversationId: (route.query.id as string) || data.value.conversationId,
  })

  if (res?.code === 0) {
    ElMessage({ type: 'success', message: 'Thank you for your feedback' })
    feedbackRef.value.hide()
    emits('evaluateSuccess', { rating, feedbackMsg: text, messageId: data.value.msgID })
  } else {
    ElMessage({ type: 'error', message: res?.message || 'Something went wrong' })
  }
}
const copy = () => {
  useFeedbackRequest({
    messageId: data.value.msgID,
    rating: 'THUMBS_NO',
    conversationId: (route.query.id as string) || data.value.conversationId,
    feedbackAction: 'COPY',
  })
  const clipboard = new ClipboardJS('.copy-icon', {
    text: function () {
      return data.value.content
    },
  })

  clipboard.on('success', () => {
    clipboard.destroy()
    ElMessage({ type: 'success', message: '复制成功' })
  })
}
</script>

<style scoped lang="scss">
.feedback {
  padding: 9px 0 10px;

  gap: 12px;

  i {
    cursor: pointer;
  }
  i.active {
    :deep(svg) {
      path,
      polygon {
        fill: #1f2937;
      }
    }
  }
}
</style>
<style lang="scss">
.el-popover.bad-tip-popover {
  padding: 16px;
  background: #ffffff;
  box-shadow: 0 12px 24px 0 rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  max-width: fit-content;
  .bad-tip {
    width: fit-content;
    .title {
      font-family: MiSans-Medium;
      font-size: 16px;
      color: #1f2937;
      line-height: 24px;
      font-weight: 500;

      margin-block-end: 16px;
    }
    .tip-item-title {
      font-family: MiSans-Normal;
      font-size: 14px;
      color: #777e91;
      line-height: 20px;
      margin-block-end: 9px;
    }

    .tip-item {
      gap: 8px;
      flex-wrap: wrap;
      margin-block-end: 16px;

      .content {
        user-select: none;
        cursor: pointer;
        font-family: MiSans-Normal;
        font-size: 12px;
        color: #1c2848;
        line-height: 20px;

        padding: 6px 10px;
        background: #ffffff;
        border: 1px solid #e1e1e1;
        border-radius: 2px;
      }
    }
    .content.active {
      background: rgba(61, 74, 198, 0.08);
      border: 1px solid #3d4ac6;
      color: #3d4ac6;
    }

    .other-input {
      white-space: nowrap;
      gap: 8px;

      .el-input {
        font-family: MiSans-Normal;
        font-size: 12px;
      }

      .button {
        cursor: pointer;
        background: #3d4ac6;
        border-radius: 4px;
        padding: 8px 16px;

        font-family: MiSans-Regular;
        font-size: 14px;
        color: #ffffff;
        line-height: 24px;
      }
      button:active {
        background: #313ca5;
      }
    }
  }
}
</style>
