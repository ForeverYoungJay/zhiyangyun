import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/auth/LoginView.vue'
import MainLayout from '../layouts/MainLayout.vue'
import OverviewView from '../views/assets/OverviewView.vue'
import BuildingsView from '../views/assets/BuildingsView.vue'
import FloorsView from '../views/assets/FloorsView.vue'
import RoomsView from '../views/assets/RoomsView.vue'
import BedsView from '../views/assets/BedsView.vue'
import QrCodesView from '../views/assets/QrCodesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', redirect: '/assets/overview' },
        { path: '/assets/overview', component: OverviewView },
        { path: '/assets/buildings', component: BuildingsView },
        { path: '/assets/floors', component: FloorsView },
        { path: '/assets/rooms', component: RoomsView },
        { path: '/assets/beds', component: BedsView },
        { path: '/assets/qrcodes', component: QrCodesView },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.path !== '/login' && !localStorage.getItem('token')) return '/login'
})

export default router
