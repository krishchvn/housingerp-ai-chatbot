/**
 * ChatWidgetConnected.tsx
 *
 * Drop this file into the existing HousingERP React app.
 * It reads auth + user context from the Redux store so you
 * don't need to pass props manually everywhere.
 *
 * Mount once in your root layout (e.g. DefaultLayout.tsx or App.tsx).
 */

import { useSelector } from "react-redux";
import ChatWidget from "../ChatWidget";

// ── Adjust these selectors to match your actual Redux state shape ─────────────
// Run `console.log(store.getState())` in browser devtools to confirm field names.

interface RootState {
  auth: {
    token: string;           // JWT token — check your Redux auth slice
    isAuthenticated: boolean;
  };
  user: {
    userId: number;
    societyId: number;
    buildingId?: number;
    flatId?: number;
  };
}

export default function ChatWidgetConnected() {
  const { token, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { userId, societyId, buildingId, flatId } = useSelector((state: RootState) => state.user);

  // Only render for logged-in residents
  if (!isAuthenticated || !token || !userId || !societyId) return null;

  return (
    <ChatWidget
      userId={userId}
      societyId={societyId}
      buildingId={buildingId}
      flatId={flatId}
      authToken={token}
    />
  );
}
