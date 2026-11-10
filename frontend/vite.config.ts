import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// host: '127.0.0.1' -- mac dinh Vite chi bind vao ::1 (IPv6), nen go
// http://127.0.0.1:5173 se KHONG vao duoc. Chi dinh ro IPv4 de trinh duyet
// va backend (CORS khai bao 127.0.0.1) deu truy cap duoc.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: false,
  },
});