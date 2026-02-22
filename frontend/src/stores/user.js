import {defineStore} from "pinia";
import {ref} from "vue";
import valentine from "daisyui/theme/valentine/index.js";

export const useUserStore = defineStore('user',()=>{
    const id = ref(1) //响应式变量 是否登录
    const username = ref('zqy')
    const photo = ref('http://127.0.0.1:8000/media/user/photos/1_4ec4741a48.png')
    const profile = ref('热爱你的生活')
    const accessToken = ref('11')

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
    }
})

