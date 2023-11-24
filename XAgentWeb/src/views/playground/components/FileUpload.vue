<template>
  <div class="file-uploader-wrapper">
      <el-upload
            accept=".txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .png, .jpeg, .gif, .py, .zip"
            v-model:file-list="fileList"
            class="upload-demo"
            :limit="5"
            action="test"
            ref="uploadFileRef"
            :on-change="handleChange"
            :on-preview="handlePreview"
            :on-remove="handleRemove"
            :auto-upload="true"
            :http-request="uploadFile"
            :multiple="true"
            :on-success="handleSuccess"
          >
          <template #trigger>
              <el-button type="primary"
                :icon="Upload"
                :disabled="fileList.length === 5">
                Upload Files
              </el-button>
          </template>
          <template #tip>
              <div class="el-upload__tip">
                You can upload up to 5 files of up to 1MB each. 
                <br>
                .txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .png, .jpeg, .gif, .py, .zip formats are supported.
              </div>
          </template>
      </el-upload>
  </div>
</template>

<script lang="ts" setup>
import { Upload } from '@element-plus/icons-vue';
import axios from 'axios';
import type { UploadInstance, UploadProps, UploadUserFile } from 'element-plus';
import { ref } from 'vue';

import { ElMessage } from 'element-plus';

const fileList = ref<UploadUserFile[]>([ ])
const uploadFileRef = ref<UploadInstance | null>(null)
const uploadFinished = ref(false)

const BACKEND_URL = (
  import.meta.env.VITE_BACKEND_URL as string
  ).replace(/\/api/, '');
  
const url = '/api/workspace/upload';  

const handleChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
}

// watch(() => fileList.value, (newVal) => {

//   let pattern = /\.([a-zA-Z0-9]+)$/;
//   let allowFileType = ['png', 'jpeg', 'gif', 'pdf', 'txt', 'pptx', 'xlsx', 'doc', 'ppt', 'xls', "py", "zip"]
//   let allowList:any = [],allowTag = true,tipFileName = ``
//   // 校验文件类型
//   for (let i = 0; i < newVal.length;i++) {
//     let fileName = newVal[i].name
//     let match = fileName.match(pattern);
    
//     if (match) {
//       let file_type = match[1];
//       if (allowFileType.indexOf(file_type) == -1) {
//         allowTag = false
//         tipFileName = fileName
//       } else {
//         allowList.push(newVal[i])
//       }
//       } else {
//         allowList.push(newVal[i])
//     }
//   }
//   if (!allowTag) {
//     ElMessage({ 
//         type: 'warning',
//         message: `The  file "${tipFileName}" type is not supported`
//     });
//   }
//   fileList.value = allowList
// });

const configStore = useConfigStore()


const uploadFile = (param: any) => {
  const formData = new FormData();

  const userStore = useUserStore()
  const { userInfo } = storeToRefs(userStore)
  userInfo.value = userStore.getUserInfo;

  console.log("params.file == ", param.file);

  formData.append('files',  param.file as File);
  formData.append('user_id', userInfo.value.user_id as string);
  formData.append('token', userInfo.value.token as string);

  axios.post(url , formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 5000
  }).then((res) => {
    if(res.data.success === true) {
      const _file = res.data.data.file_list as object[];
      configStore.addFiles(_file);
      uploadFinished.value = true;
      ElMessage({ 
        type: 'success',
        grouping: true,
        message: "upload successful!"
    });
    } else {
      ElMessage({ 
        type: 'error',
        grouping: true,
        message: res?.data?.message || "upload fiald"
    });
    }
  }).catch((err) => {
    ElMessage({ 
        type: 'error',
        grouping: true,
        message: "upload failed"
    });
  })
}

const uploadNow = () => {
  uploadFileRef.value?.submit();
}
const handleSuccess = (sutaus:any) => {
  console.log('upload success',sutaus)
}
const handleRemove = (file: UploadUserFile) => {
  console.log("file onremove")
  console.log(fileList.value);
}

const handlePreview = (file: UploadUserFile) => {
  console.log("file onpreview")
  console.log(file);
}

</script>

<style scoped lang="scss">
.file-uploader-wrapper {
padding: 20px 20px 12px 20px;
background: rgba(255,255,255,0.40);
width: 100%;
max-width: 800px;
box-shadow: inset 0 1px 3px 1px #FFFFFF;
border-radius: 12px;
height: auto;
position: relative;

:deep(button) {
  background-color: #3D4AC6;

  i.el-icon {
    color: #FFFFFF;
  }
}

:deep(.el-upload__tip) {
  font-family: 'PingFangSC-Regular';
  font-size: 14px;
  color: #676C90;
  letter-spacing: 0;
  line-height: 26px;
  font-weight: 400;
  margin-top: 10px;
  margin-bottom: 0px;
}

:deep(.el-button--primary) {
  span {
    color: #FFFFFF;
  }
}

:deep(.is-disabled) {
  span {
    color: #3D4AC6;
  }
}

.upload-demo :deep(.is-disabled) {

  span {
    color: #fff;
  }
}


}
</style>