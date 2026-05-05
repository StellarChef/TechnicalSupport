export default function Card({ title, children }) {
  return (
    <section className="rounded-app bg-white p-5 shadow-card">
      <h3 className="mb-4 text-lg font-bold text-appBlack">{title}</h3>
      {children}
    </section>
  );
}
