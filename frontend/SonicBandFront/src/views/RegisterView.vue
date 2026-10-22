<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const name = ref('')
const email = ref('')
const password = ref('')
const router = useRouter()

const handleRegister = () => {
  // La logique pour créer l'utilisateur sera ajoutée ici
  console.log('Tentative de création de compte pour :', name.value, email.value)
}

const goToLogin = () => {
  // Redirection vers la vue de connexion
  router.push('/')
}
</script>

<template>
  <div class="page-wrapper">
    <div class="register-container">
      
      <!-- En-tête -->
      <div class="brand">
        <span class="logo-icon">I</span>
        <span class="logo-text">sonicBand</span>
      </div>

      <!-- Titres -->
      <h1 class="title">Créer un compte</h1>
      <p class="subtitle">Un seul compte pour tous tes groupes.</p>

      <!-- Formulaire d'inscription -->
      <form @submit.prevent="handleRegister" class="register-form">
        
        <!-- Champ Nom affiché -->
        <div class="form-group">
          <label for="name">Nom affiché</label>
          <input 
            type="text" 
            id="name" 
            v-model="name" 
            placeholder="Paul" 
            required 
          />
        </div>

        <!-- Champ Adresse e-mail -->
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

        <!-- Champ Mot de passe -->
        <div class="form-group">
          <label for="password">Mot de passe</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="8 caractères minimum" 
            minlength="8"
            required 
          />
        </div>

        <!-- Bouton principal -->
        <button type="submit" class="btn-primary">Créer mon compte</button>
      </form>

      <!-- Lien de retour à la connexion -->
      <div class="login-section">
        <p>
          Déjà un compte ? 
          <a href="#" @click.prevent="goToLogin" class="login-link">Se connecter</a>
        </p>
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
.register-container {
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

/* Titres */
.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: #121212;
}

.subtitle {
  font-size: 0.95rem;
  color: #666;
  margin-bottom: 2rem;
}

/* Formulaire */
.register-form {
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

/* Bouton principal */
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

/* Lien "Déjà un compte" */
.login-section {
  text-align: center;
  margin-top: 2.5rem;
}

.login-section p {
  font-size: 0.95rem;
  color: #666;
}

.login-link {
  color: #3867d6; /* Bleu de la maquette */
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}
</style>