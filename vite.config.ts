import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
  base: "/invest/",
  plugins: [
    svelte(), 
    Icons({
      compiler: 'svelte', 
    })
  ],
})

