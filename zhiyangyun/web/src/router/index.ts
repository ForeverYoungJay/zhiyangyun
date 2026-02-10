import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import MainLayout from '../layouts/MainLayout.vue'
import AssetRoomPage from '../pages/asset-room/AssetRoomPage.vue'
import ElderLifecyclePage from '../pages/elder/ElderLifecyclePage.vue'
import CareStandardPage from '../pages/care/CareStandardPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginPage },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', component: AssetRoomPage },
        { path: 'elders', component: ElderLifecyclePage },
        { path: 'care', component: CareStandardPage }
      ]
    }
  ]
})

router.beforeEach((to, _, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) return next('/login')
  next()
})

export default router
