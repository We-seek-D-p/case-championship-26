import js from '@eslint/js'
import ts from 'typescript-eslint'
import vue from 'eslint-plugin-vue'
export default ts.config(
  { ignores: ['.nuxt/**', '.output/**', 'node_modules/**', 'public/**'] },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs['flat/essential'],
  { files: ['**/*.vue'], languageOptions: { parserOptions: { parser: ts.parser } } },
  {
    rules: { 'no-undef': 'off', 'vue/multi-word-component-names': 'off' },
    languageOptions: {
      globals: {
        defineNuxtConfig: 'readonly',
        defineAppConfig: 'readonly',
        useRuntimeConfig: 'readonly',
        useFetch: 'readonly',
        ref: 'readonly',
        computed: 'readonly',
        watch: 'readonly',
        onMounted: 'readonly',
        onBeforeUnmount: 'readonly',
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        URL: 'readonly',
        Blob: 'readonly',
        ResizeObserver: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        File: 'readonly',
      },
    },
  },
)
