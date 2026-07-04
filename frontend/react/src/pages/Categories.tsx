import { useState, useEffect, useCallback } from "react";
import { fetchCategories } from "../api/categories";
import { createCategory, updateCategory } from "../api/categories";
import { apiDelete } from "../api/client";
import { EditIcon, DeleteIcon, CloseIcon } from "../components/Icons";
import type { Category } from "../types/transaction";
import type { CategoryFormData } from "../types/category";

export default function Categories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Category | null>(null);
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState<"income" | "expense">("expense");

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    fetchCategories()
      .then(setCategories)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const incomeCategories = categories.filter((c) => c.type === "income");
  const expenseCategories = categories.filter((c) => c.type === "expense");
  const displayed = tab === "income" ? incomeCategories : expenseCategories;

  function openCreate() {
    setEditing(null);
    setShowModal(true);
  }

  function openEdit(cat: Category) {
    setEditing(cat);
    setShowModal(true);
  }

  async function handleSave(data: CategoryFormData) {
    setSaving(true);
    try {
      if (editing) {
        await updateCategory(editing.id, data);
      } else {
        await createCategory(data);
      }
      setShowModal(false);
      setEditing(null);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this category?")) return;
    try {
      await apiDelete(`/api/v1/categories/${id}/`);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  return (
    <div className="categories-page">
      <div className="page-header">
        <h2>Categories</h2>
        <button className="btn-primary" onClick={openCreate}>+ Add Category</button>
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="category-tabs">
        <button
          className={`category-tab ${tab === "expense" ? "active" : ""}`}
          onClick={() => setTab("expense")}
        >
          Expense ({expenseCategories.length})
        </button>
        <button
          className={`category-tab ${tab === "income" ? "active" : ""}`}
          onClick={() => setTab("income")}
        >
          Income ({incomeCategories.length})
        </button>
      </div>

      <div className="card">
        {loading ? (
          <div className="page-loader">Loading...</div>
        ) : displayed.length === 0 ? (
          <p className="empty-state">No {tab} categories found</p>
        ) : (
          <div className="category-grid">
            {displayed.map((cat) => (
              <div key={cat.id} className="category-card">
                <div className="category-card-left">
                  <span className="category-card-icon">{cat.icon || "—"}</span>
                  <div className="category-card-info">
                    <span className="category-card-name">{cat.name}</span>
                    <div className="category-card-meta">
                      <span className="category-dot" style={{ background: cat.color }} />
                      {cat.is_default && <span className="status-badge status-safe">Default</span>}
                    </div>
                  </div>
                </div>
                <div className="category-card-actions">
                  {!cat.is_default && (
                    <>
                      <button className="btn-icon" onClick={() => openEdit(cat)} title="Edit">
                        <EditIcon />
                      </button>
                      <button className="btn-icon btn-icon-danger" onClick={() => handleDelete(cat.id)} title="Delete">
                        <DeleteIcon />
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <CategoryModal
          editing={editing}
          saving={saving}
          onSave={handleSave}
          onClose={() => { setShowModal(false); setEditing(null); }}
        />
      )}
    </div>
  );
}

function CategoryModal({ editing, saving, onSave, onClose }: {
  editing: Category | null;
  saving: boolean;
  onSave: (data: CategoryFormData) => Promise<void>;
  onClose: () => void;
}) {
  const [name, setName] = useState(editing?.name || "");
  const [type, setType] = useState<"income" | "expense">(editing?.type || "expense");
  const [color, setColor] = useState(editing?.color || "#6366f1");
  const [icon, setIcon] = useState(editing?.icon || "");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!name.trim()) {
      setError("Category name is required");
      return;
    }
    try {
      await onSave({
        name: name.trim(),
        type: editing ? editing.type : type,
        color,
        icon: icon.trim(),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{editing ? "Edit Category" : "Add Category"}</h3>
          <button className="btn-icon" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}

          {!editing && (
            <div className="form-group">
              <label>Type</label>
              <div className="type-toggle">
                <button
                  type="button"
                  className={`type-btn ${type === "expense" ? "active expense" : ""}`}
                  onClick={() => setType("expense")}
                >
                  Expense
                </button>
                <button
                  type="button"
                  className={`type-btn ${type === "income" ? "active income" : ""}`}
                  onClick={() => setType("income")}
                >
                  Income
                </button>
              </div>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="cat-name">Name</label>
            <input id="cat-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Freelance" required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cat-color">Color</label>
              <div className="color-input-wrap">
                <input
                  id="cat-color"
                  type="color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="color-input"
                />
                <input
                  type="text"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  maxLength={7}
                  placeholder="#6366f1"
                  className="color-text"
                />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="cat-icon">Icon (emoji)</label>
              <input id="cat-icon" type="text" value={icon} onChange={(e) => setIcon(e.target.value)} placeholder="e.g. 💼" maxLength={2} />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : editing ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
