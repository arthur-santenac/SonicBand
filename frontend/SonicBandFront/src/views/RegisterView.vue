<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'
import '@/assets/auth.css'
import { useAuthStore } from '@/stores/auth'

const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

const handleRegister = async () => {
  error.value = ''
  loading.value = true
  try {
    await auth.register(name.value, email.value, password.value)
    router.push('/home')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/')
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-brand">
      <img :src="logo" alt="" class="auth-logo" />
      <span class="auth-brand-name">sonicBand</span>
    </div>

    <div class="auth-card">
      <h1 class="auth-title has-subtitle">Créer un compte</h1>
      <p class="auth-subtitle">Un seul compte pour tous tes groupes.</p>

      <form class="auth-form" @submit.prevent="handleRegister">
        <p v-if="error" class="auth-error" role="alert">{{ error }}</p>

        <div class="field">
          <label for="name">Nom affiché</label>
          <input
            id="name"
            v-model="name"
            type="text"
            placeholder="Paul"
            autocomplete="nickname"
            required
          />
        </div>

        <div class="field">
          <label for="email">Adresse e-mail</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="paul@exemple.fr"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label for="password">Mot de passe</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="8 caractères minimum"
            minlength="8"
            autocomplete="new-password"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Création…' : 'Créer mon compte' }}
        </button>
      </form>

      <div class="auth-footer">
        <a href="#" class="link" @click.prevent="goToLogin">Déjà un compte ? Se connecter</a>
      </div>
    </div>
  </div>
</template>