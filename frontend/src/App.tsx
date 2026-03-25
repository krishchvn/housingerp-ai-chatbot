import ChatWidget from "./ChatWidget";

export default function App() {
  return (
    <>
      <div style={styles.page}>
        <h1 style={styles.title}>🏠 HousingERP</h1>
        <p style={styles.sub}>Your society management platform</p>
      </div>
      <ChatWidget />
    </>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    background: "#0f172a",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  },
  title: { color: "#fff", fontSize: 36, fontWeight: 700, margin: 0 },
  sub: { color: "#64748b", marginTop: 8, fontSize: 16 },
};
