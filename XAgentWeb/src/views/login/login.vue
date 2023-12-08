<template>
  <section class="login-wrapper flex-row" :class="{ 'show-form': isShowForm }">
    <section class="login flex-column flex-center">
      <div class="login-box flex-column">
        <div class="login-title">X-Agent</div>

        <div v-if="isSignup" class="signup-wrapper flex-column">
          <span>{{ loginForm.email }}</span>
          <span class="msg">
            Your registration is successful and is being queued. 
            After the review is passed, 
            we will invite you to experience it by text message as soon as possible.
          </span>

          <div class="main-btn flex-row flex-center" @click="backHome">
            Back Home
          </div>
        </div>

        <div v-else class="login-form flex-column">
          <div
            class="input-box flex-row"
            :data-error="!isExistPhone ? loginFormStatus.email.code[mobileCode] : 'Wrong phone number format'"
            :class="[
              { focus: focusType === 'email' },
              { empty: loginFormStatus.email.isRequired },
              { 'format-error': loginFormStatus.email.isFormatError && !loginFormStatus.email.isRequired },
            ]"
          >
            <input
              v-model="loginForm.email"
              type="text"
              class="plain-input email-input"
              placeholder="Enter your email address please"
              autocomplete="off"
              @focus="focusType = 'email'"
              @blur="focusType = ''"
              @input="changePhone"
            />
          </div>
          <div
            class="input-box flex-row"
            data-error="Wrong verification code format"
            :class="[
              { empty: loginFormStatus.code.isRequired },
              { disabled: !isExistPhone },
            ]"
          >
            <input
              v-model="loginForm.token"
              class="plain-input code-input"
              type="password"
              placeholder="Enter your email token please"
              autocomplete="off"
              @blur="focusType = ''"
              @keydown.enter="throttledSubmit"
            />
              <p 
                class="verify-code"
                v-show="false"
                :style="codeTime.smsCode === 0 ? 'cursor:pointer' : ''" @click="getVerifyCode">
                {{ codeTime.smsCode === 0 ? 'Get SMS verification code' : `Resend in (${codeTime.smsCode}s)` }}
              </p>
          </div>

          <el-button 
            class="main-btn flex-row flex-center"
            @click="throttledSubmit"
            :loading="isSubmitLoading"
            >
            Login
          </el-button>

          <div 
              v-show="false"
              class="main-btn flex-row flex-center"
              @click="registerNow"> 
            申请
          </div>
        </div>

        <div class="plain-row flex-row">
          <span style="margin-right: 10px;">No account yet? </span>
          <span class="link-btn" @click="showApplyForm">Sign up</span>
        </div>
        <!-- TODO: 暂不提供OpenAI api-key 接口, by zhpeng -->
        <!-- <div class="plain-row flex-row">
          <span style="margin-right: 10px;">Have an OpenAI token already? </span>
          <span class="link-btn" @click="freeTrial">Registration-Free Trial</span>
        </div> -->

        <!-- TODO: Login with Wechat -->
        <div class="tip" v-show="false">
         Your applying for registration constitutes your acceptance of our
          <a target="_blank" href="javascript:void(0)">
            Terms of Service
          </a> And
          <a target="_blank" href="javascript:void(0)">
            Privacy Policy
          </a>
        </div>
      </div>

      <!-- <div class="beian flex-row">
        <a href="http://beian.miit.gov.cn/" target="_blank">京ICP备2023004350号-1</a>
      </div> -->
    </section>
    <section class="apply-form">
      <ApplyForm :mobile="loginForm.email" @signup-success="signupSuccess" />
    </section>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';
import { reactive, ref } from 'vue';
import ApplyForm from './component/ApplyForm.vue';
import throttle from '/@/utils/throttle';

const router = useRouter()
const userStore = useUserStore()
const authStore = useAuthStore()

interface LoginFormInf {
  email: string
  token: string
}

const isSubmitLoading = ref(false)

const DEFAULT_ACCOUNT = 'Guest'
const DEFAULT_PSWD = 'xagent'

const loginForm = reactive<LoginFormInf>({
  email: DEFAULT_ACCOUNT,
  token: DEFAULT_PSWD,
  // email: "",
  // token: "",
})

const loginFormStatus: any = reactive({
  email: {
    isRequired: false,
    isFormatError: false,
    errorMsg: 'Wrong phone number format',
    code: { 
      1017: 'Unregistered, please apply for registration',
      1021: 'Reviewing',
      1014: 'Wrong phone number format',
    },
  },
  code: { isRequired: false, isFormatError: false },
})
const isSubmit = ref(false)
const focusType = ref<keyof LoginFormInf | ''>('')
const error = reactive({ email: false, code: false })

const mobileCode = ref(0)
const isExistPhone = ref(true)

const changePhone = async () => {
  // loginFormStatus.code.isFormatError = false
  // loginFormStatus.code.isRequired = false
  // if (loginForm.email.length === 11) {
  //   // TODO:  Check if phone number exists
  //   const res: any = await useCheckPhoneRequest({ mobile: loginForm.email })

  //   if (res?.code !== 0) {
  //     mobileCode.value = res?.code
  //     isExistPhone.value = false
  //     loginFormStatus.email.isFormatError = true
  //   } else {
  //     isExistPhone.value = true
  //     loginFormStatus.email.isFormatError = false
  //   }
  // } else {
  //   loginFormStatus.email.isFormatError = false
  // }
}

const registerNow = async () => {
  const res: any = await useRegisterRequest({
    email: loginForm.email,
    name: '张三'
  });
  if (res?.success) {
    ElMessage({ type: 'success', message: 'Register successfully' })
    localStorage.setItem('token', res.data.token);
    loginForm.token = res.data.token;
  } else if(res?.status === 'failed') {
    ElMessage({ type: 'error', message: 'Failed to register' })
  } else  {
    ElMessage({ type: 'error', message: res?.message })
  }
}

const codeTime = reactive({ smsCode: 0 })
const getVerifyCode = async () => {
  // if (!isExistPhone || codeTime.smsCode !== 0) return

  // loginFormStatus.email.isRequired = loginForm.email === ''
  // if (loginFormStatus.email.isRequired) return
  // loginFormStatus.email.isFormatError = !useValidPhone(loginForm.email)
  // if (loginFormStatus.email.isFormatError) return

  // codeTime.smsCode = 59
  // const timer = setInterval(() => {
  //   codeTime.smsCode--
  //   if (codeTime.smsCode === 0) clearInterval(timer)
  // }, 1000)
  // // TODO: Obtain verification code
  const res: any = await useMobileCodeRequest({ mobile: loginForm.email, scene: 2 })
  if (res?.code === 0) {
    ElMessage({ type: 'success', message: 'Send successfully' })
    ;(document.querySelector('.code-input') as HTMLElement)?.focus()
  } else {
    ElMessage({ type: 'error', message: (res?.message  || 'Send failed') })
  }
}

const freeTrial = () => {
  let _T = prompt("Please enter your OpenAI token", "");
  if (_T != null) {
    // reg validate the token 
    console.log(_T);
    // if token is valid, then login and mock user info
  } else {
    ElMessage({ type: 'error', message: 'Your OpenAI token is invalid' });
  }
}

const isShowForm = ref(false)
const showApplyForm = () => {
  isShowForm.value = true
}


const submit = async () => {

  if (!isExistPhone.value) return

  isSubmitLoading.value = true

  loginFormStatus.email.isRequired = loginForm.email === ''
  loginFormStatus.code.isRequired = loginForm.token === ''

  // if (!useValidPhone(loginForm.email)) {
  //   loginFormStatus.email.isFormatError = true
  //   return
  // } else {
  //   loginFormStatus.email.isFormatError = false
  // }

  // if (
  //   loginFormStatus.email.isRequired ||
  //   loginFormStatus.email.isFormatError ||
  //   loginFormStatus.code.isRequired ||
  //   loginFormStatus.code.isFormatError
  // ) {
  //   return
  // }

  const param = {
    email: loginForm.email,
    token: loginForm.token,
  }

  const res: any = await useLoginRequest(param);
  isSubmitLoading.value = false

  if (res?.success || res?.message === 'success') {
    
    userStore.setUserInfo(res?.data)
    authStore.setLoginState(true)
    authStore.setLoginToken(res?.data?.token)

    ElMessage({ type: 'success', message: 'Login successfully' })
    router.push({ path: '/playground' })
  } else {
    ElMessage({ type: 'error', message: (res?.message || 'Login failed') })
  }
}

// const throttledSubmit = throttle(submit, 4000)
const throttledSubmit = submit


const backHome = () => {
  router.push({ path: '/' })
}

const isSignup = ref(false)
const signupSuccess = (state: boolean) => {
  isShowForm.value = false
  if (state) {
    isSignup.value = true
  }
}
</script>

<style scoped lang="scss">
.login-wrapper {
  min-height: 100%;
  height: 100%;
  overflow: hidden;
  background: linear-gradient(180deg, #f4f3f8 0%, #eaedf6 100%);
}

.login-wrapper.show-form {
  .login {
    transform: translateX(-100%);
  }
  .apply-form {
    transform: translateX(-100%);
  }
}
.login {
  margin: auto;
  flex-shrink: 0;
  width: 100%;
  // height: 100%;
  height: 100vh;
  transform: none;
  transition: transform 0.2s ease-in 0.1s;

  .login-box {
    background: rgba(255, 255, 255, 0.72);
    border-radius: 4px;
    margin: 0 auto;
    padding: var(--size-2448) 64px 1rem;
    width: 100%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;

    .login-title {
      margin-block-end: var(--size-1632);
      width: 100%;
      font-family: MiSans-Medium;
      font-size: 30px;
      color: var(--color-1);
      text-align: center;
      font-weight: var(--font-weight-5);
    }
    .signup-wrapper {
      gap: 20px;
      margin-block-end: 48px;
      font-family: MiSans-Normal;
      font-size: 16px;
      color: #1f2937;


      .msg {
        width: 320px;
        margin: 0 auto;
        color: #a4a9b6;
      }
    }

    .login-form {
      gap: 20px;
      margin-block-end: 48px;
      width: 100%;
      text-align: center;
      .input-box {
        width: 100% !important;
        min-width: 280px;
        max-width: 400px;
        // padding: 14px 12px;
        border: 1px solid #eeeeee;
        border-radius: 4px;
        position: relative;
        margin: 0 auto;

        input {
          width: 100% !important;
          margin: 0 auto;
          flex: 1;
          padding: 14px 12px;
          border: 0;
          background: transparent;
          font-family: MiSans-Normal;
          font-weight: 400;
          line-height: 22px;

          &::-webkit-input-placeholder {
            color: #a4a9b6;
          }

          &:focus-visible {
            outline: none;
          }
        }

        .verify-code {
          user-select: none;
          width: min-content;
          white-space: nowrap;
          margin: 0 12px;
          align-self: center;

          font-family: MiSans-Normal;
          font-size: 14px;
          color: #a4a9b6;
        }
      }

      .input-box.focus {
        border-color: #3d4ac6;
        box-shadow: 0 0 2px 0 rgba(61, 74, 198, 0.4);
      }

      .input-box.format-error {
        &::after {
          content: attr(data-error);
          position: absolute;
          right: 0;
          top: 50%;
          transform: translateY(-50%);

          color: var(--color-danger);
          font-size: 14px;
          padding: 0 12px;
        }
      }

      .input-box.empty {
        input:empty::-webkit-input-placeholder {
          color: var(--color-danger);
        }
      }

      .input-box.submit {
        input:empty::-webkit-input-placeholder {
          color: var(--color-danger);
        }
      }

      .input-box.disabled {
        color: #a4a9b6;
        input {
          color: #a4a9b6;
        }
        &::before {
          content: '';
          position: absolute;
          width: 100%;
          height: 100%;
          background: rgb(0 0 0 / 10%);
        }
      }
    }

    .main-btn {
      margin: 10px auto 0 auto;
      cursor: pointer;
      user-select: none;
      background: #3d4ac6;
      border-radius: 4px;
      width: 100%;
      max-width: 400px;
      min-width: 280px;
      height: 50px;
      font-family: MiSans-Normal;
      color: #ffffff;
    }

    .plain-row {
      width: 100%;
      justify-content: center;
      margin-bottom: 12px;

      font-family: MiSans-Normal;
      font-size: 16px;
      color: #777e91;
      line-height: 22px;

      .link-btn {
        cursor: pointer;
        color: #1f2937;
        text-decoration: underline;
      }
    }

    .tip {
      font-family: MiSans-Normal;
      font-size: 12px;
      color: #6f7481c0;
      text-align: center;
      line-height: 16px;
      font-weight: 400;
      margin-top: 10px;
      max-width: 350px;

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

  .beian {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);

    font-family: PingFangSC-Regular;
    font-size: 12px;
    font-weight: 400;

    gap: 24px;
    a {
      color: #ccc;
      text-decoration: none;
    }
    a:active {
      color: #eee;
    }
  }
}
.apply-form {
  width: 100%;
  height: 100%;
  flex-shrink: 0;
  transform: none;
  transition: transform 0.3s ease-in;

  overflow-y: auto;
  padding: 40px 0;
  margin: auto;
}

input::placeholder {
  font-size: 12px;
}

p.verify-code {
  font-size: 12px !important;
  color: #7896e2 !important;
}
</style>
