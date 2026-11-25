<template>
  <AppLayout>
    <main class="main-content">
      <button type="button" class="back" @click="retour">‹ Retour</button>
      <header class="content-header">
        <h1>Mes disponibilités</h1>
        <p class="subtitle">
          Ajoute tes plages horaires libres. Elles sont partagées avec tous tes groupes.
        </p>
      </header>
      <MesDisponibilites v-model:lundi="lundi" />
    </main>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import MesDisponibilites from '@/components/MesDisponibilites.vue'
import { lundiDe } from '@/utils/semaine'

const router = useRouter()
const lundi = ref(lundiDe())

function retour() {
  if (window.history.state?.back) router.back()
  else router.push({ name: 'home' })
}
</script>

<style scoped>
.main-content {
  flex: 1;
  min-width: 0;
}

.back {
  border: none;
  background: none;
  padding: 0;
  margin-bottom: 12px;
  font-family: inherit;
  font-size: 0.95rem;
  color: #65676b;
  cursor: pointer;
}

.back:hover {
  color: #1c1e21;
}

.content-header {
  margin-bottom: 16px;
}

h1 {
  font-size: 2rem;
  margin: 0;
  font-weight: 700;
  color: #000;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 4px 0 0;
  color: #65676b;
  font-size: 0.95rem;
}
</style>
