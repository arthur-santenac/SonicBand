<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'
import '@/assets/auth.css'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/home')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-brand">
      <img :src="logo" alt="" class="auth-logo" />
      <span class="auth-brand-name">sonicBand</span>
    </div>

    <div class="auth-card">
      <h1 class="auth-title">Connexion</h1>

      <form class="auth-form" @submit.prevent="handleLogin">
        <p v-if="error" class="auth-error" role="alert">{{ error }}</p>

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
          <div class="field-row">
            <label for="password">Mot de passe</label>
            <a href="#" class="link" @click.prevent>Mot de passe oublié ?</a>
          </div>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Connexion…' : 'Se connecter' }}
        </button>
      </form>

      <hr class="auth-divider" />

      <div class="auth-alt">
        <p>Pas encore de compte ?</p>
        <button type="button" class="btn btn-secondary" @click="goToRegister">
          Créer un compte
        </button>
      </div>
    </div>
  </div>
</template>