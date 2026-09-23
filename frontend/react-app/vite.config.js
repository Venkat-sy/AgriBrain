import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { handleChatRequest } from './server/chatHandler.js';

export default defineConfig({
    plugins: [
        react(),
        {
            name: 'api-chat-plugin',
            configureServer(server) {
                server.middlewares.use('/api/chat', (req, res) => {
                    handleChatRequest(req, res);
                });
            },
        },
    ],
    base: '/',
    server: {
        port: 5173,
        host: '0.0.0.0',
        open: true,
    },
    build: {
        outDir: 'dist',
        sourcemap: false,
        minify: 'esbuild',
        rollupOptions: {
            output: {
                manualChunks: {
                    'vendor': ['react', 'react-dom', 'react-router-dom'],
                    'charts': ['recharts'],
                    'animations': ['framer-motion'],
                    'icons': ['lucide-react'],
                },
            },
        },
    },
    esbuild: {
        loader: 'jsx',
        include: /src\/.*\.jsx?$/,
        exclude: [],
    },
    optimizeDeps: {
        esbuildOptions: {
            loader: {
                '.js': 'jsx',
            },
        },
    },
});
