interface subtask {
    node_id: number | string
    task_id: number | string
    name: string
    goal: string | null
    inner: any[]
    isFinished?: boolean
    isRunning?: boolean
    refinement: any
    isShowRefinement?: boolean
}


interface TaskState {
    current_subtask_index : number
    current_inner_index : number
    subtasks: subtask[]
    isCompleted: boolean
    isAutoMode: boolean
}

export const useTaskStore = defineStore('task', {
    state: (): TaskState => {
        return {
            subtasks: [],
            current_subtask_index: 0,
            current_inner_index: 0,
            isCompleted: false,
            isAutoMode: false,
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
        

        addInner(data: any) {
            if(this.isCompleted) {
                return 
            }
            let index_1 = this.subtasks.findIndex((item) => item.task_id === data.current);
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


        nextsubtask(data: any) {
            if(this.isCompleted) {
                return 
            } 

            let index_2 = this.subtasks.findIndex((item) => item.task_id === data.current);
            
            console.log("index_2", index_2);

            if(index_2 < 0 || index_2 === this.subtasks.length - 1) {
                // last element or not found
                this.subtasks.concat(data.data);
                
            } else {
                // not last element and index + 1 is available
                const tail_num = this.subtasks.length - index_2;
                this.subtasks.splice(index_2, tail_num, ...data.data);     
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

        getSubtasks(): subtask[] {
            return this.subtasks
        }
    }
})


