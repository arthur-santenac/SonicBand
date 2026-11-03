<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TheWelcome from '../components/TheWelcome.vue'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push('/')
}
</script>

<template>
  <main>
    <header class="home-header">
      <p v-if="auth.user">
        Connecté en tant que {{ auth.user.nom_user }} ({{ auth.user.email_user }})
      </p>
      <button type="button" @click="handleLogout">Se déconnecter</button>
    </header>
    <TheWelcome />
  </main>
</template>

<style scoped>
.home-header {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
</style>