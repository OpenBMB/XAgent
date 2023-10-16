import { ChatMsgInfoInf, HistoryInf } from '/#/talk-type'
import { reactive } from 'vue'

interface MsgInfoInf {
  msgID: string
  content: string
  parentMsgID: string
}

interface Setting{
  mode?: string
  agent?: string
  plugins?: Array<string>
  temperature?: number
}

interface HistoryTalkState {
  history: Map<string, MsgInfoInf>
  historyArr?: Array<any>
  sharedArr?: Array<any>
  currentInput: string
  isRequestingAi: boolean
  setting: Map<string, Setting>
  msgInfoList: MsgInfoInf[]
  isShouldRefreshHistory: boolean
}

export const useHistoryTalkStore = defineStore('talk', {
  state: (): HistoryTalkState => {
    return {
      history: new Map(),
      historyArr: [],
      sharedArr: [],
      currentInput: '',
      isRequestingAi: false,
      msgInfoList: [],
      setting: new Map(),
      isShouldRefreshHistory: false,
    }
  },
  getters: {
    getHistoryTalk() {},
    getCurrentInput(): string {
      return this.currentInput
    },
    getArrHistory(): Array<any> {
      return this.historyArr || []
    },
    getSharedArr(): Array<any> {
      return this.sharedArr || []
    },
    getisRequestingAi(): boolean {
      return this.isRequestingAi
    },
    getMsgInfo(): MsgInfoInf[] {
      return this.msgInfoList
    },
  },
  actions: {
    setHistoryChat(conversationId: string, val: any) {
      if (!Array.isArray(val)) {
        val = [val]
      }
      this.history.set(conversationId, val)
    },

    setHistoryArr(val: any[]) {
      this.historyArr = val
    },

    setSharedArr(val: any[]) {
      this.sharedArr = val
    },

    setHistoryArrItem(val: any, index: number) {
      if(!this.historyArr) return
      this.historyArr[index] = val
    },

    pushHistoryArr(val: any) {
      this.historyArr && this.historyArr.push(val)
    },


    setSetting(conversationId: string, val: Setting) {
      this.setting.set(conversationId, val)
    },
    updateHistoryChat(conversationId: string, msgID: string, val: ChatMsgInfoInf) {
      const chat: any = this.history.get(conversationId)
      if (chat) {
        const currentChat = chat.find((item: ChatMsgInfoInf) => item.msgID === msgID)
        currentChat.childrenIds = val.childrenIds
      }
    },
    addSubTask(conversationId: string, msgID: string, tasksId: string, dataID: string, val: any, isAll?: boolean) {
      const chat: any = this.history.get(conversationId);
      console.log("running on addSubTask", chat, conversationId, msgID, tasksId, dataID, val, isAll)
      if (chat) {
        const currentChat = chat.find((item: ChatMsgInfoInf) => item.msgID === msgID)
        if(currentChat) {
          //currentChat.subTasks[currentChat.subTasks.length -1].complete = true
          if(!isAll) {
            const obj = reactive(val)
            currentChat.subTasks.push(obj)
          }
          const currentTask = currentChat.subTasks.find((taskItem: any) => {return taskItem.tasksId === tasksId})
          if(currentTask) {
            const currentTool = currentTask.tools.find((toolItem: any) => {return toolItem.id === dataID})
            if(currentTool) {
              currentTool.complete = true
            }
          }
        }
        
      }
    },
    getCurrentMessage(conversationId: string, msgID: string) {
      const chat: any = this.history.get(conversationId)
      if (chat) {
        const currentChat = chat.find((item: ChatMsgInfoInf) => item.msgID === msgID)
        return currentChat
      }
    },
    requestComplete(conversationId: string, msgID: string, tasksId: string, dataID: string,) {
      const chat: any = this.history.get(conversationId)
      if(chat) {
        const currentChat = chat.find((item: ChatMsgInfoInf) => item.msgID === msgID)
        if(currentChat) {
          currentChat['complete'] = true
          const currentTask = currentChat.subTasks.find((taskItem: any) => {return taskItem.tasksId === tasksId})
          if(currentTask) {
            const currentTool = currentTask.tools.find((toolItem: any) => {return toolItem.id === dataID})
            if(currentTool) {
              currentTool.complete = true
            }
          }
        }
        
      }
    },
    updateInferencing(conversationId: string, msgID: string, tasksId: string, dataID: string, isComplete: boolean) {
      const chat: any = this.history.get(conversationId)
      if (chat) {
        const currentChat = chat.find((item: ChatMsgInfoInf) => item.msgID === msgID)
        if(currentChat) {
          const currentTask = currentChat.subTasks.find((taskItem: any) => {return taskItem.tasksId === tasksId})
          if(currentTask) {
            if(isComplete) {
              currentTask.complete = true
            }
            let tag = 0
            const currentTool = currentTask.tools.find((toolItem: any, index: number) => {
              if(toolItem.id === dataID) {
                tag = index
                return true
              }
              return toolItem.id === dataID
            })
            if(currentTool) {
              if(tag < currentTask.tools.length - 1) {
                currentTask.tools[tag + 1].unClickbel = false
              }
              currentTool.complete = true
            }
          }
        }
        
      
      }
    },
    pushHistoryChat(conversationId: string, val: ChatMsgInfoInf) {
      const chat: any = this.history.get(conversationId)
      if (chat) {
        chat.unshift(val)
        this.setHistoryChat(conversationId, chat)
      }
    },
    getHistoryChat(conversationId: string): any {
      return this.history.get(conversationId)
    },
    getSetting(conversationId: string): any {
      return this.setting.get(conversationId)
    },
    setCurrentInput(val: string) {
      this.currentInput = val
    },
    getCurrentHistory(id?: string): any {
      // if (!id) return ''
      // return this.history.find((item: HistoryInf) => item.conversationId === id) || ''
    },
    setisRequestingAi(val: boolean): any {
      this.isRequestingAi = val
    },
    clearHistory() {
      this.history = new Map()
    },
    clearSetting(){
      this.setting = new Map()
    },
    setMsgInfo(val: MsgInfoInf[]) {
      this.msgInfoList = val
    },
    setisShouldRefreshHistory(val: boolean) {
      this.isShouldRefreshHistory = val
    },
  },
})
