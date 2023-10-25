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

                <span
                    v-if="isString(ExecutionResults)"
                    class="result-viewer-btn-wrapper"
                >
                    <el-button  
                        plain 
                        size="small"
                        @click="handleViewResult"
                        :icon="View">
                        View Result
                    </el-button>
                </span>

                <json-viewer 
                    v-else
                    class="end-subtask-info-content-item-viewer"
                    :expand-depth="0"
                    :expanded="false"
                    :value="ExecutionResults"
                ></json-viewer>
            </div>

            <div class="end-subtask-info-content-item" 
                v-if="isPythonNoteBook"
                >
                <span class="end-subtask-info-content-item-title">
                    Tool Input Code:
                </span>
                <span  class="code-viewer-btn-wrapper">
                    <el-button plain size="small"
                        :icon="View"
                        @click="handleViewCode"
                    >View code</el-button>
                </span>
            </div>

            <div class="end-subtask-info-content-item">
                <span class="end-subtask-info-content-item-title">
                    Command Status:
                </span>
                <span class="command-status-wrapper">
                    <span class="command-status-prefix-icon">
                        {{ 
                            getCommandStatusIcon(CommandStatus)
                        }}
                    </span>
                    <span
                        style="padding-top: 8px; margin-left: 5px;"
                        :class="{
                            'command-status-success': getCommanStatus(CommandStatus) === 1,
                            'command-status-fail': getCommanStatus(CommandStatus) === -1,
                            'command-status-other': getCommanStatus(CommandStatus) === 0,
                        }">
                            {{ CommandStatus }}
                        </span>
                </span>
            </div>

            <image-viewer  :dataList="imagesArr" v-if="false" />

            <el-dialog
                    v-model="isModalOpen"
                    :title="modalTitle"
                    width="70%"
                    :modal="true"
                    align-center
                    :before-close="handleClose"
                    destroy-on-close
                >
                <code-viewer :value="viewedCodeStr" :isShowLineNum="showLineNum" />
                <template v-slot:footer>
                    <el-button 
                        type="primary"
                        @click="isModalOpen = false">Close</el-button>
                </template>
            </el-dialog>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, } from 'vue'
import ImageViewer from './ImageViewer.vue'
import CodeViewer from './CodeViewer.vue'
import { View } from '@element-plus/icons-vue'

const props = defineProps(['data'])

const isModalOpen = ref(false)
const viewedCodeStr = ref("")

const handleClose = (done: any) => {
    isModalOpen.value = false
    done()
}

const objectToString = (obj: any) => {
    return JSON.stringify(obj)
}

const modalTitle = ref<string>("");
const showLineNum = ref<boolean>(true);

const isString = (obj: any) => {
    return typeof obj === 'string'
}

const getImagesArrFromResult = (data: any) => {
    if(typeof data === 'string') {
        return [];
    }
    if( Array.isArray(data) ) {
        return data.filter((item: any) => {
            return item.media_type.startsWith('image/')
        }).map((item: any) => {
            return {
                name: item.file_name,
                data: item.file_data,
                type: item.file_name.split('.').pop(),
            }
        });
    } else {
        return []
    }
}

const getCommanStatus = (status: string) => {
    if(status.includes('SUCCESS') || status.includes('Success')) {
        return 1;
    } else if(status.includes('FAIL') || status.includes('Fail')) {
        return -1;
    } else {
        return 0;
    }
}

const getCommandStatusIcon = (status: string) => {
    if(status.includes('SUCCESS') || status.includes('Success')) {
        return '✅';
    } else if(status.includes('FAIL') || status.includes('Fail')) {
        return '❌';
    } else {
        return '⏳';
    }
}

const imagesArr = computed(
    () => getImagesArrFromResult(props.data.ExecutionResults)
);
const isPythonNoteBook = computed(
    () => props.data.tool_name.includes('PythonNotebook_execute_cell') ? true : false);

const CommandName = computed(
    () => props.data.tool_name);

const Arguments = computed(
    () => props.data.tool_input);

const ExecutionResults = computed(
    () => {
        return props.data.tool_output;
    });

const CommandStatus = computed(
    () => props.data.tool_status_code);

const ToolInputCode = computed(
    () => props.data.tool_input?.code || '');

const handleViewResult = () => {
    modalTitle.value  = "Execution Results"
    isModalOpen.value = true;
    showLineNum.value = false;
    viewedCodeStr.value = ExecutionResults.value
}
const handleViewCode = () => {
    modalTitle.value  = "Tool Input Code"
    isModalOpen.value = true;
    showLineNum.value = true;
    viewedCodeStr.value = ToolInputCode.value
}

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

:deep(.el-dialog__body) {
    padding: 0 10px 10px 10px !important;
    height: 70vh;
}

.result-viewer-btn-wrapper, .code-viewer-btn-wrapper {
    height: auto;
    padding-top: 5px;
}

.command-status-wrapper {
    padding-top: 8px;
}

.command-status-success {
    color: #67C23A;
}

.command-status-fail {
    color: #F56C6C;
}

.command-status-other {
    color: #909399;
}
</style>
