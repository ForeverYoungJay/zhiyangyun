import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import MainLayout from '../layouts/MainLayout.vue'
import AssetRoomPage from '../pages/asset-room/AssetRoomPage.vue'
import ElderLifecyclePage from '../pages/elder/ElderLifecyclePage.vue'
import CareStandardPage from '../pages/care/CareStandardPage.vue'
import M4MedicationPage from '../pages/modules/M4MedicationPage.vue'
import M5MealPage from '../pages/modules/M5MealPage.vue'
import M6HealthPage from '../pages/modules/M6HealthPage.vue'
import M7BillingPage from '../pages/modules/M7BillingPage.vue'
import OA1ShiftPage from '../pages/modules/OA1ShiftPage.vue'
import OA2ApprovalPage from '../pages/modules/OA2ApprovalPage.vue'
import OA3NotificationPage from '../pages/modules/OA3NotificationPage.vue'
import OA4TrainingPage from '../pages/modules/OA4TrainingPage.vue'
import B1MiniappPage from '../pages/modules/B1MiniappPage.vue'
import B2FamilyPage from '../pages/modules/B2FamilyPage.vue'
import B3DashboardPage from '../pages/modules/B3DashboardPage.vue'
import ShopInventoryPage from '../pages/modules/ShopInventoryPage.vue'

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
        { path: 'care', component: CareStandardPage },
        { path: 'm4', component: M4MedicationPage },
        { path: 'm5', component: M5MealPage },
        { path: 'm6', component: M6HealthPage },
        { path: 'm7', component: M7BillingPage },
        { path: 'oa1', component: OA1ShiftPage },
        { path: 'oa2', component: OA2ApprovalPage },
        { path: 'oa3', component: OA3NotificationPage },
        { path: 'oa4', component: OA4TrainingPage },
        { path: 'b1', component: B1MiniappPage },
        { path: 'b2', component: B2FamilyPage },
        { path: 'b3', component: B3DashboardPage },
        { path: 'shop', component: ShopInventoryPage }
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
