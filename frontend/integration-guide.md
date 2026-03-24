# Wiring ChatWidget into HousingERP

## Step 1 — Copy files into HousingERP frontend

Copy these two files into your existing React app's `src/components/` folder:
- `ChatWidget.tsx`
- `ChatWidgetConnected.tsx`

```
housingerp-frontend/src/
└── components/
    └── ChatWidget/
        ├── ChatWidget.tsx
        └── ChatWidgetConnected.tsx
```

## Step 2 — Install axios (if not already installed)

```bash
npm install axios
```

## Step 3 — Add env variable

In the HousingERP frontend `.env` file, add:

```
VITE_CHATBOT_API=http://localhost:8000
```

For production:
```
VITE_CHATBOT_API=https://your-chatbot-backend.com
```

## Step 4 — Fix Redux selectors in ChatWidgetConnected.tsx

Open `ChatWidgetConnected.tsx` and check the Redux state shape.
In your browser, open DevTools Console and run:

```js
// Paste this while on the HousingERP app (logged in)
window.__REDUX_DEVTOOLS_EXTENSION__ && console.log(window.__store?.getState())
```

Or install Redux DevTools browser extension and inspect state.

Match the selectors to your actual state:
```tsx
// Example — change these to match YOUR Redux slices:
const token     = useSelector((state) => state.auth.token)
const userId    = useSelector((state) => state.auth.user.userId)
const societyId = useSelector((state) => state.auth.user.societyId)
const flatId    = useSelector((state) => state.auth.user.flatId)
const buildingId = useSelector((state) => state.auth.user.buildingId)
```

## Step 5 — Mount in your layout

Find the root layout file (usually `DefaultLayout.tsx`, `MainLayout.tsx`, or `App.tsx`).
It wraps all authenticated pages. Add one line:

```tsx
// DefaultLayout.tsx (or wherever your sidebar/navbar lives)
import ChatWidgetConnected from "../components/ChatWidget/ChatWidgetConnected";

export default function DefaultLayout({ children }) {
  return (
    <div>
      <Sidebar />
      <main>{children}</main>

      {/* Add this — renders floating chat button for all pages */}
      <ChatWidgetConnected />
    </div>
  );
}
```

## Step 6 — Run both servers

Terminal 1 — Backend:
```bash
cd housingerp-ai/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Terminal 2 — Frontend (existing HousingERP app):
```bash
npm run dev
```

## Step 7 — Test

1. Log in as a resident
2. You should see a 💬 green floating button (bottom-right)
3. Click it and type: "The water supply in my flat is very low"
4. Bot should classify → ask for confirmation → submit complaint

## Troubleshooting

| Problem | Fix |
|---|---|
| CORS error | Make sure `CORS_ORIGINS` in backend `.env` includes your frontend URL |
| Token not found | Check Redux selector path in `ChatWidgetConnected.tsx` |
| Bot not classifying correctly | Check Groq API key is valid in backend `.env` |
| Complaint not submitting | Confirm `HOUSINGERP_API_BASE` is correct in backend `.env` |
