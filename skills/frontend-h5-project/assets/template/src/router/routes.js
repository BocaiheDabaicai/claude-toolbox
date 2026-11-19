// 路由路径配置，新增页面在此登记
// meta.hideBottomNav: 二级页不显示底部导航（顶栏提供返回 + 首页图标）
// meta.backTo: 顶栏返回的上一级路由名；数组表示多个合法上级，优先回退历史，否则跳第一项
// meta.fullHeight: 页面自己管理底部留白（如固定高度双栏布局），DefaultLayout 不再叠加底栏 padding
const PlaceholderView = () => import('@/views/PlaceholderView.vue')

export default [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: PlaceholderView,
        meta: { title: '首页' },
      },
      {
        path: 'category',
        name: 'category',
        component: PlaceholderView,
        meta: { title: '分类' },
      },
      {
        path: 'cart',
        name: 'cart',
        component: PlaceholderView,
        meta: { title: '购物车' },
      },
      {
        path: 'profile',
        name: 'profile',
        component: PlaceholderView,
        meta: { title: '我的' },
      },
      {
        // 二级页示例：隐藏底栏，返回时优先回到首页
        path: 'detail/:id',
        name: 'detail',
        component: PlaceholderView,
        meta: { title: '详情示例', hideBottomNav: true, backTo: 'home' },
      },
    ],
  },
]
