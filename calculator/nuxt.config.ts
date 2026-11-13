export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: '2026-11-13',
  modules: ['@nuxt/ui'],
  css: ['maplibre-gl/dist/maplibre-gl.css', '~/assets/css/main.css'],
  ui: { fonts: false },
  colorMode: { preference: 'light' },
  typescript: { strict: true },
  runtimeConfig: { public: { mapStyle: 'https://tiles.openfreemap.org/styles/positron' } },
  app: { head: { title: 'Red Wings / Маршрутный калькулятор', htmlAttrs: { lang: 'ru' } } },
})
