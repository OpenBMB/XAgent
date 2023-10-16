interface ConfigState {
    filelist: any[]
    recorder_dir: string | null
}

export const useConfigStore = defineStore('config', {
    state: (): ConfigState => {
      return {
        filelist: [],
        recorder_dir: null
      }
    },
    getters: {
        getFileList(): any[] {
            return this.filelist
        },
        getRecorderDir(): string | null {
            return this.recorder_dir
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
        }
    }
})
