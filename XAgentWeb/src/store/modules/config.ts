interface newtalkSettings {
    mode: string
    agent: string
}

interface ConfigState {
    filelist: any[]
    recorder_dir: string | null
    newtalkSettings: newtalkSettings
    input: string
}

export const useConfigStore = defineStore('config', {
    state: (): ConfigState => {
      return {
        filelist: [],
        recorder_dir: null,
        newtalkSettings: {
            mode: "",
            agent: "",
        },
        input: ""
      }
    },
    getters: {
        getFileList(): any[] {
            return this.filelist
        },
        getRecorderDir(): string | null {
            return this.recorder_dir
        },
        getNewtalkSettings(): object {
            return this.newtalkSettings
        },
        getInput(): string {
            return this.input
        }
    },
    actions: {
        addFileItem(val: any) {
            this.filelist.push(val)
        },
        addFiles(val: any[]) {
            this.filelist = this.filelist.concat(val)
        },
        setFileList(val: any[]) {
            this.filelist = val
        },
        setRecorderDir(val: string) {
            this.recorder_dir = val
        },
        resetConfig() {
            this.filelist = []
            this.recorder_dir = null
        },
        setNewtalkSettings(val: newtalkSettings) {
            this.newtalkSettings = val
        },
        setInput(val: string) {
            this.input = val
        }
    }
})
