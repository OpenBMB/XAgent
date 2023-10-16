<template>
    <div class="end-subtask-info">
        <div class="end-subtask-info-content">
            <div class="end-subtask-info-content-item">
                <span class="end-subtask-info-content-item-title">
                    Command Name:
                </span>
                <json-viewer
                class="end-subtask-info-content-item-viewer" 
                :value="CommandName"
                :expand-depth="0"
                :expanded="false"
                ></json-viewer>
            </div>
            <div class="end-subtask-info-content-item">
                <span class="end-subtask-info-content-item-title">
                    Arguments:
                </span>
                <json-viewer class="end-subtask-info-content-item-viewer" 
                :expand-depth="0"
                :expanded="false"
                :value="Arguments"></json-viewer>
            </div>
            <div class="end-subtask-info-content-item">
                <span class="end-subtask-info-content-item-title">
                    Execution Results:
                </span>
                <json-viewer class="end-subtask-info-content-item-viewer"
                    :expand-depth="0"
                    :expanded="false"
                    :value="ExecutionResults"
                    
                    ></json-viewer>
            </div>
            <div class="end-subtask-info-content-item">
                <span class="end-subtask-info-content-item-title">
                    Command Status:
                </span>
                <json-viewer class="end-subtask-info-content-item-viewer" 
                :expand-depth="0"
                :expanded="false"
                :value="CommandStatus"></json-viewer>
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

const CommandName = computed(
    () => props.data.tool_name);

const Arguments = computed(
    () => props.data.tool_input);

const ExecutionResults = computed(
    () => props.data.tool_output);

const CommandStatus = computed(
    () => props.data.tool_status_code);


</script>

<style lang="scss" scoped>
.end-subtask-info {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start ;
    .end-subtask-info-title {
        width: 100%;
        height: auto;
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
        margin-top: -10px;
    }
    .end-subtask-info-content {
        width: 100%;
        height: 90%;
        display: flex;
        flex-direction: column;
        align-items: center;
        .end-subtask-info-content-item {
            width: 100%;
            height: auto;
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            justify-content: flex-start;
            background: #FFFFFF;
            border-radius: 8px;
            
            .end-subtask-info-content-item-title {
                width: 150px;
                height: auto;
                font-size: 15px;
                letter-spacing: 0;
                line-height: 26px;
                font-weight: 500;
                margin-top: 5px
            }

            .end-subtask-info-content-item-viewer {
                width: calc(100% - 150px);
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
