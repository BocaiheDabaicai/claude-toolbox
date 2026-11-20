// 路由路径配置，新增页面在此登记
// meta.hideBottomNav: 二级页 / 管理台 / PC 组不显示底部导航
// meta.backTo: 顶栏返回的上一级路由名；数组表示多个合法上级，优先回退历史，否则跳第一项
// meta.fullHeight: 页面自己管理底部留白（如固定高度双栏布局），DefaultLayout 不再叠加底栏 padding
//
// 三种界面形态按路由组选择布局：
// - H5 会员端：DefaultLayout（max-w-md + 底部导航）
// - 管理后台：AdminLayout（侧边栏 + 顶栏 + max-w-7xl）
// - PC 站点：PcLayout（顶部导航 + 宽内容区）
const PlaceholderView = () => import('@/views/PlaceholderView.vue')

export default [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { hideBottomNav: true },
    children: [
      {
        path: '',
        name: 'admin-home',
        component: () => import('@/views/admin/AdminDashboardView.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'customers',
        name: 'admin-customers',
        component: () => import('@/views/admin/AdminCustomersView.vue'),
        meta: { title: '客户管理' },
      },
    ],
  },
  {
    path: '/site',
    component: () => import('@/layouts/PcLayout.vue'),
    meta: { hideBottomNav: true },
    children: [
      {
        path: '',
        name: 'site-home',
        component: () => import('@/views/pc/PcHomeView.vue'),
        meta: { title: 'PC 首页' },
      },
    ],
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
