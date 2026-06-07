Frontend (Vite + React) quickstart

# Setup
Run from repo root:

npm create vite@latest frontend -- --template react
cd frontend
npm install

# Tailwind
npm i -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Run dev
npm run dev

# Notes
- Add i18n files in src/i18n
- Use TanStack Query for data fetching
- Configure VITE_API_URL in .env
