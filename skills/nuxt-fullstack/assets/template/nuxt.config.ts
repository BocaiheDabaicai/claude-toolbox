import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-11-20',
  devtools: { enabled: false },
  css: ['@fontsource-variable/noto-sans-sc', '~/assets/css/main.css'],
  vite: {
    plugins: [tailwindcss()],
  },
  app: {
    head: {
      htmlAttrs: { lang: 'zh-CN' },
      title: '__PROJECT_TITLE__',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#1F5FA8' },
      ],
    },
    pageTransition: { name: 'page', mode: 'out-in' },
  },
  runtimeConfig: {
    databaseUrl: '',
    sessionSecret: '',
    sessionCookieName: 'app_session',
    public: {
      appName: '__PROJECT_TITLE__',
      secureCookies: true,
    },
  },
  typescript: {
    strict: true,
    typeCheck: false,
  },
})
