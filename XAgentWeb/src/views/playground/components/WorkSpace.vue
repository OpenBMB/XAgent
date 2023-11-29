<template>
    <div class="workspace-container-wrapper">
        <div class="workspace-container">
            <div class="file-list-wrapper" >
                <template 
                        v-for="(file, index) in workspaceFiles"
                        :key="index"
                    >
                    <div 
                        :class="['file-item', { 'active': file.name === currentActiveFileNames }]"
                        @click="openFile(file)"
                    >
                        <span class="file-icon">
                            <svg t="1698982978958"
                                class="icon" 
                                viewBox="0 0 1024 1024" 
                                version="1.1" 
                                xmlns="http://www.w3.org/2000/svg"
                                p-id="4011" 
                                width="15px" height="15px">
                                <path d="M842.666667 285.866667l-187.733334-187.733334c-14.933333-14.933333-32-21.333333-53.333333-21.333333H234.666667C194.133333 74.666667 160 108.8 160 149.333333v725.333334c0 40.533333 34.133333 74.666667 74.666667 74.666666h554.666666c40.533333 0 74.666667-34.133333 74.666667-74.666666V337.066667c0-19.2-8.533333-38.4-21.333333-51.2z m-44.8 44.8c-2.133333 2.133333-4.266667 0-8.533334 0h-170.666666c-6.4 0-10.666667-4.266667-10.666667-10.666667V149.333333c0-2.133333 0-6.4-2.133333-8.533333 0 0 2.133333 0 2.133333 2.133333l189.866667 187.733334z m-8.533334 554.666666H234.666667c-6.4 0-10.666667-4.266667-10.666667-10.666666V149.333333c0-6.4 4.266667-10.666667 10.666667-10.666666h311.466666c-2.133333 4.266667-2.133333 6.4-2.133333 10.666666v170.666667c0 40.533333 34.133333 74.666667 74.666667 74.666667h170.666666c4.266667 0 6.4 0 10.666667-2.133334V874.666667c0 6.4-4.266667 10.666667-10.666667 10.666666z" fill="#707070" p-id="4012"></path><path d="M640 693.333333H341.333333c-17.066667 0-32 14.933333-32 32s14.933333 32 32 32h298.666667c17.066667 0 32-14.933333 32-32s-14.933333-32-32-32zM640 522.666667H341.333333c-17.066667 0-32 14.933333-32 32s14.933333 32 32 32h298.666667c17.066667 0 32-14.933333 32-32s-14.933333-32-32-32zM341.333333 416h85.333334c17.066667 0 32-14.933333 32-32s-14.933333-32-32-32h-85.333334c-17.066667 0-32 14.933333-32 32s14.933333 32 32 32z"
                                p-id="4013"></path>
                            </svg>
                        </span>

                        <span class="file-name">{{ file.name }}</span>
                    </div>
                </template>
            </div>
        </div>
        <div class="workspace-viewer-container">
            <code-viewer 
                :value="viewedCodeStr" 
                :isShowLineNum="true"
                :readonly="true"
                :isLineWrapping = "true"
                v-if="fileTypeClassify(currentActiveFileType) === 'unknown'"
            />
            <python-notebook-viewer  
                :datasource="fileWrapper"
                v-show="fileTypeClassify(currentActiveFileType) === 'jpt'" />
            <images-viewer  
                :dataList="imagesArr"
                :isSingleFile="true"
                v-if="fileTypeClassify(currentActiveFileType) === 'img'"
            />
        </div>
    </div>
</template>

<script setup lang="ts">

import { ref, onMounted } from 'vue'
import CodeViewer from './CodeViewer.vue'
import PythonNotebookViewer from './PythonNotebookViewer.vue'
import ImagesViewer from './ImagesViewer.vue'

const viewedCodeStr = ref("")
const taskStore = useTaskStore()
const userStore = useUserStore()
const userInfo = userStore.getUserInfo;
const currentActiveFileNames = ref('')
const currentActiveFileType = ref('')
const imagesArr = ref<any[]>([])
const fileWrapper = ref<any>({})

const {
    workspaceFiles: workspaceFiles
} = toRefs(taskStore);

const fileTypeClassify = (fileType: string) => {
    if(['ipynb'].includes(fileType)) {
        return 'jpt';
    }
    if(['png', 'jpg', 'jpeg', 'gif', 'bmp'].includes(fileType)) {
        return 'img';
    } else {
        return 'unknown';
    }
}

const singleObjectToArray = (obj: any) => {
    const result = new Array(1).fill(obj);
    return result;
}

const openFile = (file: any) => {
    if(!file) return
    currentActiveFileNames.value = file.name
    currentActiveFileType.value = file.suffix
    useWorkspaceFileRequest({
        user_id: userInfo?.user_id,
        token: userInfo?.token,
        interaction_id: taskStore.currentTaskId,
        file_name: file?.name
    }).then((res: any) => {
        if(file.suffix === 'ipynb') {
            fileWrapper.value = res;
        } else if(['png', 'jpg', 'jpeg', 'gif', 'bmp'].includes(file.suffix)) {
            const rawImageResponse = res.data;
            imagesArr.value = singleObjectToArray({
                name: file.name,
                data: rawImageResponse
            });
        } else {
            viewedCodeStr.value = res.data
        }
    }).catch((err: any) => {
        viewedCodeStr.value = 'File load failed'
    })
}

onMounted(() => {
    openFile(workspaceFiles.value[0]);
})

const handleClose = (done: any) => {
    viewedCodeStr.value = ""
    done()
}
</script>

<style scoped lang="scss">
.workspace-container {
    width: 200px;
    height: 100%;
    background-color: #2a2c36;
    flex: 0 0 auto;
    right: 0;
    bottom: 20%;
    border-radius: 0 10px 10px 0;
    margin-top: 2px;
    div.active {
        background-color: #353f9e !important;
    } 

    .file-list-wrapper {
        padding: 5px;
        overflow-y: auto;
        height: 100%;
        box-sizing: border-box;

        .file-item {
            display: flex;
            align-items: center;
            padding: 3px 5px;
            border-radius: 5px;
            margin-bottom: 10px;
            background-color: #777;
            color: #fff;
            font-size: 14px;
            user-select: none;
            cursor: pointer;
            text-align: left;
            text-overflow: clip;

            span {
                text-overflow: clip;
                color: #fff;
            }

            &:hover {
                background-color: #6b89e475;
            }

            .file-icon {
                margin-right: 5px;
                color: #fff;
            }

            svg, path {
                color: #fff;
                fill: #fff;
            }

            svg {
                margin-top: 2px;
            }
        }
    }
}


:deep(.el-dialog__body) {
    padding: 0 10px 10px 10px !important;
    height: 70vh;
}

.workspace-container-wrapper {
    width: 100%;
    height: 100%;
    
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: flex-start;

    .workspace-viewer-container {
        width: 100%;
        height: 100%;
        margin-left: 5px;
        margin-top: 2px;
        border-radius: 10px;
        overflow-x: hidden;
        overflow-y: auto;
    }
}

</style>