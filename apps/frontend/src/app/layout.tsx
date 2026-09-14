import "./globals.css";

export const metadata = {
  title: "VOID | Mission Control",
  description: "Governed execution control plane",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}