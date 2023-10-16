<template>
  <div class="switch-box flex-row flex-center">
    <i :class="{ disabled: index <= 0 }" @click="prev"><icon-ep:arrow-left /></i>
    <span>{{ index + 1 }} / {{ data.childrenIds?.length }}</span>
    <i :class="{ disabled: index >= data.childrenIds.length - 1 }" @click="next"><icon-ep:arrow-right /></i>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

const emits = defineEmits<{
  (e: 'changeIndex', data: { index: number; lastId: string; currentId: string; conversationId: string }): void
}>()

const props = withDefaults(
  defineProps<{
    data: {
      msgID: string
      index: number
      conversationId: string
      childrenIds: string[]
      parentMsgID: string
    }
  }>(),
  {}
)
const { data } = toRefs(props)

const index = ref<number>(0)

watchEffect(() => {
  index.value = data.value.childrenIds?.findIndex((id) => id === data.value.msgID)
})

const prev = () => {
  if (index.value <= 0) return

  const idx = index.value - 1
  const params = {
    index: idx,
    lastId: data.value.childrenIds?.[index.value],
    currentId: data.value.childrenIds?.[idx],
    conversationId: data.value.conversationId,
  }
  index.value = idx

  emits('changeIndex', params)
}
const next = () => {
  if (index.value >= data.value.childrenIds.length - 1) return

  const idx = index.value + 1
  const params = {
    index: idx,
    lastId: data.value.childrenIds?.[index.value],
    currentId: data.value.childrenIds?.[idx],
    conversationId: data.value.conversationId,
  }
  index.value = idx

  emits('changeIndex', params)
}
</script>

<style scoped lang="scss">
.switch-box {
  color: #a4a9b6;
  gap: 4px;

  i:hover {
    user-select: none;
    cursor: pointer;
    color: #000;
  }
  i.disabled {
    cursor: default;
    color: #a4a9b6;
  }
}
</style>
