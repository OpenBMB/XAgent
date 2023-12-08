<template>
    <div class="task-refine-info">
        <div class="task-refine-info-title">
            <span>Task Refinement</span>
        </div>
        <div class="task-refine-info-content">
            <div class="task-refine-info-content-item" v-if="task_posterior_criticism">
                <span class="task-refine-info-content-item-title">Task Posterior Criticism:</span>
                <json-viewer 
                :expand-depth="0"
                :expanded="false"
                :value="task_posterior_criticism"></json-viewer>
            </div>
            <div class="task-refine-info-content-item" v-if="task_milestones">
                <span class="task-refine-info-content-item-title">Task Milestones:</span>
                <json-viewer
                :expand-depth="0"
                :expanded="false"
                :value="task_milestones"></json-viewer>
            </div>
            <div class="task-refine-info-content-item" v-if="posterior_tool_reflection">
                <span class="task-refine-info-content-item-title">Posterior Tool Reflection:</span>
                <json-viewer
                :expand-depth="0"
                :expanded="false"
                :value="posterior_tool_reflection"></json-viewer>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>

import { ref } from 'vue'

const props = defineProps(['data'])

const objectToString = (obj: any) => {
    return JSON.stringify(obj)
}

const task_posterior_criticism = computed(
    () => props?.data?.posterior_plan_reflection)
const task_milestones = computed(
    () => props?.data?.milestones)
const posterior_tool_reflection = computed(
    () => props?.data?.tool_reflection)

</script>

<style lang="scss" scoped>
.task-refine-info {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start ;
    .task-refine-info-title {
        width: 100%;
        height: 10%;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: flex-start;
        font-family: PingFangSC-Medium;
        font-size: 14px;
        color: #1C2848;
        letter-spacing: 0;
        line-height: 26px;
        font-weight: 500;
    }
    .task-refine-info-content {
        width: 100%;
        height: 90%;
        display: flex;
        flex-direction: column;
        align-items: center;
        .task-refine-info-content-item {
            width: 100%;
            height: auto;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: flex-start;
            background: #FFFFFF;
            border-radius: 8px;
            margin: 5px 0;
            padding: 8px 10px;

            .task-refine-info-content-item-title {
                width: 100%;
                height: auto;
                font-size: 15px;
                margin-left: 5px;
                flex: 0 0 auto;
                padding: 0;
                background-color: transparent;
                font-family: PingFangSC-Regular;
                text-align: left;
            }
            .task-refine-info-content-item-content {
                width: calc(100% - 150px);
                height: auto;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 15px;

            }

            :deep(.jv-code) {
                padding: 5px 5px !important;
            }
        }
    }
}

:deep(.jv-item.jv-string) {
    color: #676C90 !important;
}  

</style>
