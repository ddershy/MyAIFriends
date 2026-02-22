import {defineStore} from "pinia";
import {ref} from "vue";
import valentine from "daisyui/theme/valentine/index.js";

export const useUserStore = defineStore('user',()=>{
    const id = ref(0) //响应式变量 是否登录
    const username = ref('')
    const photo = ref('')
    const profile = ref('')
    const accessToken = ref('')
    const hasPulledUserInfo = ref(false)

    function isLogin(){//判断是否登录,登录为1
        return !!accessToken.value //必须先value，!a 用于判断a是否为空，!!用于取反
    }

    function setAccessToken(token){
        accessToken.value=token
    }

    function setUserInfo(data){
        id.value=data.user_id
        username.value=data.username
        photo.value=data.photo
        profile.value=data.profile
    }

    function logout(){
        id.value=0
        username.value=''
        photo.value=''
        profile.value=''
        accessToken.value=''
    }

    function setHasPulledUserInfo(newStatus){
        hasPulledUserInfo.value = newStatus
    }
    return { //必须全部返回
        id,
        username,
        photo,
        profile,
        accessToken,
        setAccessToken,
        setUserInfo,
        logout,
        isLogin,
        hasPulledUserInfo,
        setHasPulledUserInfo,
    }
})

