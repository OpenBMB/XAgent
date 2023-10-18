<template>
  <section class="apply flex-row flex-center">
    <div
      class="form-box flex-row flex-column"
      :class="{
        active:
          form.corporation &&
          form.email  &&
          form.industry && 
          form.name &&
          form.position,
      }"
    >
      <div class="form-title flex-row">
        <img src="" alt="" />
        <!-- by zhpeng -->
        <!-- <span>API open platform</span> -->
        <b>X-Agent</b>
        <strong>Sign up</strong>
        <span class="back" @click="goBack">
          Back
        </span>
      </div>
      <div class="form-content flex-column">
        <div class="form-field"
              data-label="Name"
              :class="
              { 
                error: form.name === ''&& isSubmit,
                focus: focusType === 'name'
              }">
          <el-input 
            v-model="form.name" 
            placeholder="Your name（For review purposes only）"
            @focus="focusType = 'name'" />
          <p class="form-field-label flex-row flex-center">
            Name
          </p>
        </div>
        <div
          class="form-field"
          data-label="Your Company/Collage Name"
          :class="{ error: form.corporation === '' && isSubmit, focus: focusType === 'corporation' }"
        >
          <el-input v-model="form.corporation" 
          @focus="focusType = 'corporation'" />
          <p class="form-field-label flex-row flex-center">Company/Collage Name</p>
        </div>
        <div class="form-field"
          data-label="Industry"
          :class="{ error: form.industry === '' && isSubmit, focus: focusType === 'industry' }">
          <el-input v-model="form.industry"
            @focus="focusType = 'industry'" />
          <p class="form-field-label flex-row flex-center">
            Industry
          </p>
        </div>
        <div class="form-field"
          data-label="Position"
          :class="{ error: form.position === '' && isSubmit, focus: focusType === 'position' }">
          <el-input v-model="form.position" 
          @focus="focusType = 'position'" />
          <p class="form-field-label flex-row flex-center">
            Position
          </p>
        </div>

        <div class="need-info flex-column">
          <div class="need-info__title flex-center flex-row">
            <span>
              Please verify following information
            </span>
          </div>

          <div
            class="form-field email"
            data-label="Company or school email"
            :class="{
              error: (form.email === '' && isSubmit) || formState.emailState,
              focus: focusType === 'email',
              'format-error': formState.emailState,
            }"
          >
            <el-input v-model="form.email" @focus="focusType = 'email'" @input="checkEmail" />
            <p class="form-field-label-required flex-row flex-center">Company or school email</p>
          </div>

        </div>
      </div>
      <div class="form-footer flex-column">
        <el-button 
            class="submit-btn flex-row flex-center"
            :disabled="formState.emailState || isSignUpComplete"
            :loading="isSignUpLoading"
            @click="submit">
          Submit Application
        </el-button>
        <div class="tip" v-show="false">
          Your Applying for using service constitutes your acceptance of the 
           <a target="_blank" href="/terms">
            User Terms
          </a> And <a target="_blank" href="/privacy">
            Privacy Policy
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';

const emits = defineEmits<{ (e: 'signupSuccess', data: boolean): void; (e: 'cancelSignup'): void }>()
const props = withDefaults(defineProps<{ mobile: string | number; isShow?: boolean }>(), { mobile: '', isShow: false })
const mobile = toRef(props, 'mobile')
const form = reactive<any>({
  name: '',
  corporation: '',
  position: '',
  industry: '',
  email: '',
})

const goBack = () => {
  formState.emailState = false
  focusType.value = 'name'
  emits('signupSuccess', false)
}

const focusType = ref('name')
const isSignUpLoading = ref(false)
const formState = reactive({ emailState: false, mobileState: false })

const codeTime = reactive({ smsCode: 0, emailCode: 0 })

const getVerifyCode = async (type: string) => {
  let res: any
  if (type === 'mobile' && codeTime.smsCode === 0) {
    checkPhone()
    if (formState.mobileState) return
    codeTime.smsCode = 59
    const timer = setInterval(() => {
      codeTime.smsCode--
      if (codeTime.smsCode === 0) clearInterval(timer)
    }, 1000)
    res = await useMobileCodeRequest({ mobile: form.mobile, scene: 1 })
  }

  if (type === 'email' && codeTime.emailCode === 0) {
    checkEmail()
    if (formState.emailState) return
    codeTime.emailCode = 59
    const timer = setInterval(() => {
      codeTime.emailCode--
      if (codeTime.emailCode === 0) clearInterval(timer)
    }, 1000)
    res = await useEmailCodeRequest({ email: form.email })
  }

  if (res?.code === 0) {
    ElMessage({ type: 'success', message: 'Verification code sent successfully' })
  } else {
    ElMessage({ type: 'error', message: (res?.message || 'Verification code sent failed') })
  }
}


const checkPhone = () => {
  formState.mobileState = !useValidPhone(form.mobile as string)
}
const checkEmail = () => {
  formState.emailState = !useValidEmail(form.email)
}

const isSubmit = ref(false)
const isSignUp = ref(false)
const isSignUpComplete = ref(false)

const submit = async () => {

  const checkResult = Object.values(form).every((item: any) => item.length !== 0)

  isSubmit.value = true

  if (!checkResult) return

  isSignUpLoading.value = true

  if (formState.emailState) return
  const res = await useSignUpRequest(form)

  isSignUpLoading.value = false

  if (res?.success === true) {
    isSignUp.value = true
    emits('signupSuccess', isSignUp.value)
    isSignUpComplete.value = true
    ElMessage({ 
      type: 'success', 
      message: 'Please check your email for the verification and back to login page'
    })
  } else {
    ElMessage({ type: 'error', message: (res?.message || 'Sign up failed') })
  }
}
</script>

<style scoped lang="scss">

.apply {
  width: 100%;
  overflow-y: auto;

  .form-box {
    background: #fff;
    border-radius: 4px;
    margin: 0 auto;
    padding: 40px 64px 0;

    .form-title {
      justify-content: flex-start;
      font-family: MiSans-Medium;
      font-size: 18px;
      color: #1c2848;
      line-height: 24px;
      font-weight: 500;
      margin-bottom: 32px;

      strong {
        color: #3d4ac6;
        margin-left: 10px;
      }

      .back {
        font-size: 12px;
        margin-left: auto;
        cursor: pointer;
        line-height: 1;
        align-self: flex-end;
        font-family: 'MiSans-Normal';
      }
    }
    .form-content {
      gap: 16px;
      .form-field {
        width: 320px;
        border: 1px solid #eeeeee;
        border-radius: 4px;
        position: relative;

        padding: 4px 12px 4px;

        font-family: MiSans-Normal;
        font-size: 16px;
        color: #a4a9b6;
        font-weight: 400;

        // &::before {
        //   user-select: none;
        //   content: attr(data-label);
        //   position: absolute;
        //   top: -8px;
        //   left: 12px;
        //   background: #fff;
        //   width: fit-content;
        //   height: 16px;
        //   box-shadow: none;
        //   padding: 0 2px;

        //   font-family: MiSans-Normal;
        //   font-size: 12px;
        //   color: #1f2937;
        //   font-weight: 400;
        // }

        & .form-field-label-required {
          gap: 4px;
          user-select: none;
          position: absolute;
          top: -8px;
          left: 12px;
          font-family: MiSans-Normal;
          font-size: 12px;
          color: #1f2937;

          background: #fff;
          width: fit-content;
          height: 16px;
          box-shadow: none;
          padding: 0 2px;

          &::before {
            content: '*';
            color: red;
            position: relative;
            height: 12px;
            top: 50%;
            transform: translateY(-50%);
          }
        }

        & .form-field-label {
          gap: 4px;
          user-select: none;
          position: absolute;
          top: -8px;
          left: 12px;
          font-family: MiSans-Normal;
          font-size: 12px;
          color: #1f2937;

          background: #fff;
          width: fit-content;
          height: 16px;
          box-shadow: none;
          padding: 0 2px;

        }

        &:focus {
          outline: none;
        }

        :deep(.el-input__wrapper) {
          padding: 0;
          box-shadow: none;
          &.is-focus {
            box-shadow: none;
          }

          .el-input__inner {
            height: 38px;
          }
          .el-input__inner::placeholder {
            font-family: MiSans-Normal;
            font-size: 12px;
            color: #a4a9b6;
            font-weight: 400;
          }
        }

        .verify-code {
          user-select: none;
          width: min-content;
          white-space: nowrap;
          align-self: center;

          font-family: MiSans-Normal;
          font-size: 14px;
          color: #a4a9b6;

          &.active,
          &:hover {
            color: #1f2937;
          }
        }
      }
      .form-field.focus {
        border-color: #3d4ac6;
        box-shadow: 0 0 2px 0 rgba(61, 74, 198, 0.4);
      }

      .form-field.error {
        border-color: red;
        box-shadow: 0 0 2px 0 rgb(255 0 0 / 40%);
      }

      .form-field.disabled {
        background-color: #f5f7fa;
        &::before {
          background-color: transparent;
          background: linear-gradient(0deg, #f5f7fa 0 56%, transparent 52% 100%);
        }
      }

      .form-field.format-error {
        display: flex;
        align-items: center;
        gap: 8px;
        &::after {
          content: 'Wrong email address format';
          white-space: nowrap;
          color: red;
          font-family: MiSans-Normal;
          font-size: 12px;
        }
      }
      .form-field.mobile.format-error::after {
        content: 'Wrong phone number format';
        font-size: 12px;
        white-space: nowrap;
        color: red;
        font-family: MiSans-Normal;
        font-size: 12px;
      }

      .need-info {
        gap: 24px;
        margin-top: 8px;

        .need-info__title {
          font-family: MiSans-Normal;
          font-size: 16px;
          color: #a4a9b6;
          background: linear-gradient(90deg, #eee 0 30%, transparent 30% 70%, #eee 70%);
          background-size: 100% 1px;
          background-repeat: no-repeat;
          background-position: center;

          span {
            background: #fff;
            padding: 0 8px;
            font-size: 12px !important;
          }
        }
      }
    }

    .form-footer {
      gap: 24px;
      padding-bottom: 16px;
      .submit-btn {
        cursor: pointer;
        background: #a0a2b4;
        border-radius: 4px;
        width: 320px;
        height: 50px;
        margin-top: 24px;

        font-family: MiSans-Normal;
        color: #ffffff;

        // &:hover {
        //   // background: #6a6fa4;
        // }
      }
      .tip {
        font-family: MiSans-Normal;
        font-size: 12px;
        color: #1c2848;
        text-align: center;
        line-height: 16px;
        font-weight: 400;
        width: 320px;

        a {
          cursor: pointer;
          font-family: MiSans-Normal;
          font-size: 12px;
          color: #1c2848;
          text-align: center;
          line-height: 16px;
          font-weight: 400;
          text-decoration: underline;
        }
      }
    }
  }
  .form-box.active {
    .submit-btn {
      background: #3d4ac6;
    }
  }
}



p.verify-code {
  font-size: 12px !important;
  color: #7896e2 !important;
}
</style>
