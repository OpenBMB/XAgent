<template>
    <codemirror
        v-model="code"
        placeholder="Code is here..."
        :style="{ height: '100%', width: '100%' }"
        :autofocus="true"
        :indent-with-tab="true"
        :tab-size="2"
        :extensions="extensions"
        :options="CodeEditorOptions"
        :lineNumbers="showLineNum"
        @ready="handleReady"
    />
  </template>
  
  <script lang="ts">

  import { defineComponent } from 'vue'
  import { Codemirror } from 'vue-codemirror'
  import { python } from '@codemirror/lang-python'
  import { oneDark } from '@codemirror/theme-one-dark'
  import { shallowRef, reactive } from 'vue'
  
  export default defineComponent({
    components: {
      Codemirror
    },
    props: {
      value: {
        type: String,
        default: ''
      },
      isShowLineNum: {
        type: Boolean,
        default: false
      },
      isLineWrapping: {
        type: Boolean,
        default: true
      },
    },
    setup(props, { emit }) {

      const code = computed(() => (props.value));
      const showLineNum = computed(() => (props.isShowLineNum));
      const extensions = [python(), oneDark]

      // Codemirror EditorView instance ref
      const view = shallowRef()

      const handleReady = (payload: any) => {
        view.value = payload.view
      }

      const CodeEditorOptions = reactive({
          lineNumbers: false,
          lineWrapping: props.isLineWrapping,
          theme: 'one-dark',
          mode: 'python',
          indentUnit: 2,
          tabSize: 2,
          indentWithTabs: true,
          autofocus: true,
          placeholder: 'Code is here...',
          lineSeparator:'\n'
      })
  
      const print = (type: any, event: any) => {
        console.log(type, event)
      } 

      watch(() => showLineNum.value, (val) => {
        CodeEditorOptions.lineNumbers = val
      });
  
      return {
        code,
        extensions,
        handleReady,
        print,
        showLineNum,
        CodeEditorOptions
      }
    }
  })
  </script>