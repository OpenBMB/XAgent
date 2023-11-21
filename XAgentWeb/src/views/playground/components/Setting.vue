<template>
  <div class="setting">
    <div class="setting_top flex-column">
      <span class="title">Hi!</span>
      <span class="title">ToolLLM&nbsp;
        <strong>XAGENT</strong>
      </span>
      <span class="sub_title">Please choose your Agent & Mode to continue.</span>
    </div>
    <div class="content flex-row">
      <div class="content-left">
        <div class="row">
          <span class="label">Agent</span>
          <el-select 
              v-model="agent" 
              class="select-input"
              placeholder="Please select">
              <el-option
                v-for="item in agentOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
        </div>
        <div class="row">
          <span class="label">Mode</span>
          <el-select 
              v-model="mode"
              class="select-input"
              placeholder="Please select">
              <el-option
                v-for="item in modeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
        </div>
       
          <!-- <el-form-item label="Plugins">
            <el-select @change="pluginsSelectChange" multiple v-model="plugins" class="m-2" placeholder="Select" size="small">
              <el-option-group
                key="device"
                label="Programming Language"
              >
                <el-option
                  v-for="item in pluginsOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <div class="item flex-row">
                    <div class="item_left">
                      <img />
                    </div>
                    <div class="item_right">
                      <img class="checkbox_normal" :class="{ checkbox_checked: item.checked }" />
                      {{ item.label }}
                    </div>
                  </div>
                </el-option>
              </el-option-group>
            </el-select>
          </el-form-item> -->
          <!-- <el-form-item label="temperature" style="padding-top: 120px;" >
            <el-slider v-model="temperature" :marks="marks" :max="1" :min="0" :step="0.01" show-input />
          </el-form-item> -->
      </div>
      <div class="content-right">
        <!-- <div class="plugin-select-info">
          <div class="info-title flex-row">
            <img />
            <span>SQL</span>
          </div>
          <div class="info-content">
            <span>这个是介绍</span>
          </div>
        </div> -->
      </div>
    </div>
  </div>
</template>
  
<script setup lang="ts">
  import { ref } from 'vue'
  import type { CSSProperties } from 'vue'
  const emit = defineEmits(['settingChange'])
  interface PluginsOption {
    label?: string
    value?: string
    checked?: boolean
  }
  interface AgentOption {
    label?: string
    value?: string

  }
  interface ModeOption{
    label?: string
    value?: string
  }
  interface Mark {
    style: CSSProperties
    label: string
  }
  type Marks = Record<number, Mark | string>
  const agent = ref('')
  const mode = ref('')

  const router = useRouter()
  // const temperature = ref(0)
  // const plugins = ref([])
  const agentOptions = ref<Array<AgentOption>>([])
  const modeOptions = ref<Array<ModeOption>>([])
  // const pluginsOptions = ref<Array<PluginsOption>>([])
  // const marks = reactive<Marks>({
  //   0: '0',
  //   0.2: '0.2',
  //   0.4: '0.4',
  //   // 0.6: {
  //   //   style: {
  //   //     color: '#1989FA',
  //   //   },
  //   //   label: '50%',
  //   // },
  //   0.6: '0.6',
  //   0.8: '0.8',
  //   1: '1',
  // })
  onMounted(()=>{
    // pluginsOptions.value = [{
    //   value: 'plugins1',
    //   label: 'plugins1',
    //   checked: false,
    // }, {
    //   value: 'plugins2',
    //   label: 'plugins2',
    //   checked: false,
    // }]
    modeOptions.value = [{
      value: 'auto',
      label: 'Auto',
    },
    {
      value: 'manual',
      label: 'Manual',
      
    }]
    // 进行数据过滤
    agentOptions.value = [
      {
        value: 'agent',
        label: 'XAgent',
      },
    ]
  })
  // const pluginsSelectChange = (datas: Array<string>) => {
  //   const result = useArrayMap(pluginsOptions.value, (i: PluginsOption) => {
  //     const {value, label} = i
  //     return {...{value, label, checked: datas.includes(i.value || '')}}
  //   } )
  //   pluginsOptions.value = result.value
  // }
  watchEffect( () => {
    // 自动监听设置内容变化  
    emit('settingChange', {
      agent: agent.value,
      mode: mode.value,
      // temperature: temperature.value,
      // plugins: plugins.value,
    })
  })

  const handleRecord = () => {
  }

</script>

<style scoped lang="scss">
  .el-form .el-select{
    width: 100%;
  }
  .setting{
    padding: 20px;
    background: rgba(255,255,255,0.40);
    box-shadow: inset 0 1px 3px 1px #FFFFFF;
    border-radius: 12px;
    width: 100%;
    max-width: 800px;
    position: relative;
    
    .title{
      font-family: PingFangSC-Semibold;
      font-size: 26px;
      color: #05073B;
      letter-spacing: 0;
      line-height: 36px;
      font-weight: 600;

      strong {
        font-weight: 800;
      }
    }
    .sub_title{
      font-family: 'PingFangSC-Regular';
      font-size: 14px;
      color: #676C90;
      letter-spacing: 0;
      line-height: 26px;
      font-weight: 400;
      margin-top: 10px;
      margin-bottom: 12px;
    }
    
    .content {
      background: #E9EAF4;
      border-radius: 8px;
      padding: 24px 0 4px 0 ;
      .content-left{
        flex: 3;
        .row{
          display: flex;
          align-items: center;
          flex-direction: row;
          margin-bottom: 20px;
          width: 100%;
          max-width: 400px;

          .select-input{
            width: 100%;
            :global(.el-input__wrapper) {
              border-radius: 8px;

              width: 100%;
            }

            option {
              width: 100%;
              max-width: 400px;
            }
          }
        }
        .label{
          width: 108px;
          padding-right: 16px;
          text-align: right;
          font-family: PingFangSC-Regular;
          font-size: 14px;
          color: #000000;
          letter-spacing: 0;
          line-height: 22px;
          font-weight: 400;
        }
      }
      .content-right{
        flex: 1;
        position: relative;
        .plugin-select-info{
          position: absolute;
          height: 200px;
          width: calc(100% - 80px);
          padding: 10px;
          left: 40px;
          bottom: 20px;
          background-color: #ddd;
        }
      }
    }
  }
  .checkbox_normal{
    height: 20px;
    width: 20px;
    background-color: #eee;
  }
  .checkbox_checked{
    background-color: #000;
  }




  .hidden-btn {
    padding: 5px 10px;
    border-radius: 5px;
    color: #3D4AC6;
    background-color: #FFFFFF;
    position: absolute;
    top: 10%;
    right: 0;
    opacity: 0;

    &:hover {
      opacity: 0.3;
      display: block;
    }
  }
</style>
<!-- <style lang="scss">

</style> -->
  