import "./globals.css";
import { AuthProvider } from "../lib/auth-context";

export const metadata = {
  title: "AI Soil Health Monitor",
  description: "AI-Based Soil Health Assessment System for Nutrient Deficiency Detection & Crop Recommendation",
};

export const viewport = {
  themeColor: "#4caf50",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body className="antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
