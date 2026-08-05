"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Item = {
  id: number;
  reference: string;
  designation: string;
  family: string | null;
  subfamily: string | null;
  unit: string;
  minimum_stock: string;
  is_active: boolean;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({
    reference: "",
    designation: "",
    family: "",
    subfamily: "",
    unit: "unité",
    minimum_stock: "0",
  });

  async function loadItems() {
    const response = await fetch(`${API_URL}/api/items`);
    if (!response.ok) throw new Error("Chargement impossible");
    setItems(await response.json());
  }

  useEffect(() => {
    loadItems().catch(() => setMessage("Impossible de joindre l’API."));
  }, []);

  const visibleItems = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return items;
    return items.filter(
      (item) =>
        item.reference.toLowerCase().includes(term) ||
        item.designation.toLowerCase().includes(term)
    );
  }, [items, search]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage("");

    const response = await fetch(`${API_URL}/api/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        family: form.family || null,
        subfamily: form.subfamily || null,
        minimum_stock: Number(form.minimum_stock),
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => null);
      setMessage(error?.detail ?? "Création impossible.");
      return;
    }

    setForm({
      reference: "",
      designation: "",
      family: "",
      subfamily: "",
      unit: "unité",
      minimum_stock: "0",
    });
    setMessage("Article créé.");
    await loadItems();
  }

  async function archiveItem(id: number) {
    if (!window.confirm("Archiver cet article ?")) return;
    const response = await fetch(`${API_URL}/api/items/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      setMessage("Archivage impossible.");
      return;
    }
    setMessage("Article archivé.");
    await loadItems();
  }

  return (
    <main>
      <h1>Articles</h1>
      <p className="muted">Création et consultation du référentiel articles.</p>

      <section className="card section">
        <h2>Créer un article</h2>
        <form className="form-grid" onSubmit={submit}>
          <label>
            Référence *
            <input
              required
              value={form.reference}
              onChange={(e) => setForm({ ...form, reference: e.target.value })}
            />
          </label>
          <label>
            Désignation *
            <input
              required
              value={form.designation}
              onChange={(e) => setForm({ ...form, designation: e.target.value })}
            />
          </label>
          <label>
            Famille
            <input
              value={form.family}
              onChange={(e) => setForm({ ...form, family: e.target.value })}
            />
          </label>
          <label>
            Sous-famille
            <input
              value={form.subfamily}
              onChange={(e) => setForm({ ...form, subfamily: e.target.value })}
            />
          </label>
          <label>
            Unité
            <input
              required
              value={form.unit}
              onChange={(e) => setForm({ ...form, unit: e.target.value })}
            />
          </label>
          <label>
            Stock minimum
            <input
              type="number"
              min="0"
              step="0.001"
              value={form.minimum_stock}
              onChange={(e) => setForm({ ...form, minimum_stock: e.target.value })}
            />
          </label>
          <button type="submit">Créer l’article</button>
        </form>
        {message && <p className="message">{message}</p>}
      </section>

      <section className="card section">
        <div className="toolbar">
          <div>
            <h2>Liste des articles</h2>
            <p className="muted">{visibleItems.length} article(s)</p>
          </div>
          <input
            className="search"
            placeholder="Rechercher une référence ou une désignation"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Référence</th>
                <th>Désignation</th>
                <th>Famille</th>
                <th>Unité</th>
                <th>Stock mini</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {visibleItems.map((item) => (
                <tr key={item.id}>
                  <td><strong>{item.reference}</strong></td>
                  <td>{item.designation}</td>
                  <td>{item.family ?? "—"}</td>
                  <td>{item.unit}</td>
                  <td>{item.minimum_stock}</td>
                  <td>
                    <button className="danger" onClick={() => archiveItem(item.id)}>
                      Archiver
                    </button>
                  </td>
                </tr>
              ))}
              {visibleItems.length === 0 && (
                <tr>
                  <td colSpan={6}>Aucun article enregistré.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
