import { createApp } from 'vue'
import '@fontsource-variable/noto-sans-sc'
import './style.css'
import App from './App.vue'
import router from './router'
import pinia from './stores'

// 路由守卫里会用到 Pinia store，必须先安装 Pinia
createApp(App).use(pinia).use(router).mount('#app')
