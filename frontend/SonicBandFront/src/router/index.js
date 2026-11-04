import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/groups/new',
      name: 'create-group',
      component: () => import('../views/CreateGroupView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/groups/:id/musiciens',
      name: 'group-musicians',
      component: () => import('../views/CreateGroupView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/groups/:id',
      name: 'group',
      component: () => import('../views/GroupView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guestOnly: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      // serveur injoignable : on garde le jeton et on laisse la page se charger
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: 'login' }
  if (to.meta.guestOnly && auth.isAuthenticated) return { name: 'home' }
})

export default router
