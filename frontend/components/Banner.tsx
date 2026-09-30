export function Banner({
  tone,
  children,
}: {
  tone: "ok" | "bad" | "warn" | "info";
  children: React.ReactNode;
}) {
  return <div className={`banner banner-${tone}`}>{children}</div>;
}
