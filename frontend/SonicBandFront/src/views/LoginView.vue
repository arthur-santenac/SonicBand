<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = () => {
  console.log('Tentative de connexion avec :', email.value)
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="page-wrapper">
    <div class="login-container">
      
      <!-- En-tête -->
      <div class="brand">
        <span class="logo-icon">I</span>
        <span class="logo-text">sonicBand</span>
      </div>

      <h1 class="title">Connexion</h1>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Adresse e-mail</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="paul@exemple.fr" 
            required 
          />
        </div>

        <div class="form-group">
          <div class="password-header">
            <label for="password">Mot de passe</label>
            <a href="#" class="forgot-password">Mot de passe oublié ?</a>
          </div>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="••••••••" 
            required 
          />
        </div>

        <button type="submit" class="btn-primary">Se connecter</button>
      </form>

      <!-- Trait de séparation léger -->
      <hr class="divider" />

      <div class="register-section">
        <p>Pas encore de compte ?</p>
        <button @click="goToRegister" type="button" class="btn-secondary">
          Créer un compte
        </button>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
/* Conteneur pour centrer la page entière */
.page-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
}

/* Bloc central contenant le formulaire */
.login-container {
  width: 100%;
  max-width: 400px; 
  padding: 2rem;
  display: flex;
  flex-direction: column;
}

/* Logo et Nom */
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2rem;
}

.logo-icon {
  background-color: #f2f2f2;
  color: #121212;
  font-weight: bold;
  font-size: 0.9rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.logo-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #121212;
}

/* Titre */
.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 2rem;
  color: #121212;
}

/* Formulaire */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #121212;
}

.password-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-password {
  font-size: 0.85rem;
  color: #3867d6; /* Bleu de la maquette */
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

/* Inputs sans bordure avec fond gris très clair */
input {
  padding: 1rem 1.2rem;
  font-size: 1rem;
  border: none;
  border-radius: 12px;
  background-color: #f7f7f7;
  outline: none;
  color: #121212;
}

input:focus {
  background-color: #eeeeee;
}

input::placeholder {
  color: #757575;
}

/* Boutons */
.btn-primary {
  margin-top: 1rem;
  padding: 1.1rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background-color: #121212;
  border: none;
  border-radius: 50px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #333333;
}

/* Ligne de séparation de la maquette */
.divider {
  border: none;
  border-top: 1px solid #f0f0f0;
  margin: 2.5rem 0;
}

.register-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.register-section p {
  font-size: 0.95rem;
  color: #666;
  margin: 0;
}

.btn-secondary {
  padding: 1.1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #121212;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 50px;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #f8f8f8;
}
</style>