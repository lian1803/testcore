import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { transform } from 'esbuild'
import fs from 'fs'
import path from 'path'

const TEST_HTML = path.resolve('C:/Users/lian1/Documents/Work/test.html')
const VIRTUAL_ID = '\0test-component'

export default defineConfig({
  plugins: [
    {
      name: 'load-html-as-jsx',
      enforce: 'pre',
      resolveId(source) {
        if (source.includes('test.html')) {
          return VIRTUAL_ID
        }
      },
      async load(id) {
        if (id === VIRTUAL_ID) {
          const source = fs.readFileSync(TEST_HTML, 'utf-8')
          const result = await transform(source, {
            loader: 'jsx',
            jsx: 'automatic',
          })
          return result.code
        }
      }
    },
    react(),
    tailwindcss(),
  ],
})
