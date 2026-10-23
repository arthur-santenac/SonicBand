<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'
import '@/assets/auth.css'

const name = ref('')
const email = ref('')
const password = ref('')
const router = useRouter()

const handleRegister = () => {
  console.log('Tentative de création de compte pour :', name.value, email.value)
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

        <button type="submit" class="btn btn-primary">Créer mon compte</button>
      </form>

      <div class="auth-footer">
        <a href="#" class="link" @click.prevent="goToLogin">Déjà un compte ? Se connecter</a>
      </div>
    </div>
  </div>
</template>
