import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EcoShopView from '../views/EcoShopView.vue'
import AboutView from '../views/AboutView.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
import BrandSearchView from '../views/BrandSearchView.vue'
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/eco-shop',
    name: 'ecoShop',
    component: EcoShopView
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView
  },
  {
    path: '/knowledge',
    name: 'knowledge',
    component: KnowledgeView
  },
  {
  path: '/brand-search',
  name: 'brandSearch',
  component: BrandSearchView
}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router