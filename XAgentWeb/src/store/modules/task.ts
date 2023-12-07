interface subtask {
    node_id: number | string
    task_id: number | string
    name: string
    goal: string | null
    inner: any[]
    isFinished?: boolean
    isRunning?: boolean
    refinement: any
    isShowRefinement?: boolean,
}


interface TaskState {
    current_subtask_index : number
    current_inner_index : number
    currentTaskId: null | string
    currentNewTalkId?: null | string
    subtasks: subtask[]
    isCompleted: boolean
    isAutoMode: boolean
    workspaceFiles: any[]
    last_step_id: null | string
}

export const useTaskStore = defineStore('task', {
    state: (): TaskState => {
        return {
            subtasks: [],
            current_subtask_index: 0,
            current_inner_index: 0,
            isCompleted: false,
            currentTaskId: null,
            currentNewTalkId: null,
            isAutoMode: false,
            workspaceFiles: [],
            last_step_id: ''
        }
    },

    actions: {
        initializeSubtasks(data: any) {
            if(this.isCompleted) {
                return 
            } 
            this.subtasks = data.data.subtasks;
            this.current_inner_index = 0
            this.current_subtask_index = 0
        },
        
        setCurrentTaskId(data: string) {
            this.currentTaskId = data
        },

        setCurrentNewTalkId(data: string) {
            this.currentNewTalkId = data
        },

        addInner(data: any) {
            if(this.isCompleted) {
                return 
            }
            let index_1 = this.subtasks.findIndex((item) => item.task_id === data.current);
            if(index_1 < 0) {
                console.log('task.ts: index_1 < 0')
                console.log('task.ts: data.', data)
                console.log('task.ts: this.subtasks', this.subtasks);
                return;
            }
            
            this.subtasks[index_1].inner.push(data.data);
            this.current_inner_index += 1
        },

        addLastInner(data: any) {
            if(this.isCompleted) {
                return 
            }
            let index_1 = this.subtasks.findIndex((item) => item.task_id === data.current);
            const temp = {
                ...data.data,
                isEndNode: true
            }
            this.subtasks[index_1].inner.push(temp);
            this.current_inner_index += 1
        },

        addRefinementInfo(data: any) {
            if(this.isCompleted) {
                return
            }
            this.subtasks[this.current_subtask_index].refinement = data.data
            this.subtasks[this.current_subtask_index].isShowRefinement = true;
        },

        setLastStepId(data: string) {
            this.last_step_id = data
        },

        nextsubtask(data: any) {
            if(this.isCompleted) {
                console.log('task.ts: task is completed')
                return;
            } 
            let index_2 = this.subtasks.findIndex((item) => data.current === item.task_id);

            if(index_2 === this.subtasks.length - 1) {
                this.subtasks.concat(data.data);
            } else {
                if(index_2 < 0) {
                    let index_3 = this.subtasks.findIndex((item) => data.current < item.task_id);
                    // keep the ascending order of subtasks
                    if(index_3 <= 0 || index_3 === this.subtasks.length - 1) {
                        this.subtasks = [...this.subtasks, ...data.data]
                    } else {
                        const tail_num = this.subtasks.length - index_3;
                        this.subtasks.splice(index_3, tail_num, ...data.data);
                    }
                } else {
                    const tail_num = this.subtasks.length - index_2;
                    this.subtasks.splice(index_2, tail_num, ...data.data);
                }                
            }
            this.current_subtask_index += 1
            this.current_inner_index = 0

        },  

        completeSubtask() {
            this.isCompleted = true
            this.current_subtask_index = this.subtasks.length - 1;
            // set current index to a number that is larger than the length of subtasks
        },

        setStepGoal(index: number, goal: string | null) {
            this.subtasks[index].goal = goal
        },

        setAutoMode(_: boolean) {
            this.isAutoMode = _
        },

        setTaskRefineInfoArray(data: any[]) {
            if(this.isCompleted) {
                return
            } else {
                data.forEach((item: any, index: number) => {
                    this.subtasks[index].refinement = item
                });
            }
        },

        setInnerItem(data: any, subtask_index: number, inner_index: number) {
            if(this.isCompleted) {
                return
            } else {
                this.subtasks[subtask_index].inner[inner_index] = data
            }
        },

        reset() {
            this.subtasks = []
            this.current_subtask_index = 0
            this.current_inner_index = 0
            this.isCompleted = false
            this.workspaceFiles = []
        },

        addWorkspaceFiles(data: any) {
            this.workspaceFiles?.push(data)
        },

        setWorkspaceFiles(data: any[]) {
            this.workspaceFiles = data
        }

    },

    getters: {

        getCurrentSubtaskIndex(): number {
            return this.current_subtask_index
        },

        getCurrentInnerIndex(): number {
            return this.current_inner_index
        },

        getGoalArray(): any[] {
            return this.subtasks.map((item) => item.goal)
        },

        getCurrentSubtask(): subtask {
            return this.subtasks[this.current_subtask_index]
        },

        getIsSubtaskCompleted(): boolean {
            return this.isCompleted
        },

        getCurrentTaskId(): string | null {
            return this.currentTaskId
        },

        getCurrentNewTalkId(): any {
            return this.currentNewTalkId
        },

        getSubtasks(): subtask[] {
            return this.subtasks
        },

        getLastStepId(): string | null {
            return this.last_step_id
        },

        getWorkspaceFiles(): any[] {
            return this.workspaceFiles || []
        },

        getIsAutoMode(): boolean {  
            return this.isAutoMode
        }
    }
})


