import { useEffect, useState } from 'react';
import { apiFetch } from '../../api/client';
import { Product } from '../../types';
import { useCart } from '../../hooks/useCart';

export default function ProductCatalog() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [addedMsg, setAddedMsg] = useState<string | null>(null);

  const { add } = useCart();

  useEffect(() => {
    apiFetch<Product[]>('/api/inventory/products')
      .then(setProducts)
      .catch(err => setError(err.message || 'Failed to load products'))
      .finally(() => setLoading(false));
  }, []);

  const handleAdd = (p: Product) => {
    add({
      id: p.id,
      name: p.name,
      price: p.price,
      quantity: 1
    });

    setAddedMsg(`${p.name} added to cart`);

    // Auto-hide after 2 seconds
    setTimeout(() => setAddedMsg(null), 2000);
  };

  if (loading) return <p className="text-gray-500">Loading products…</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!products.length) return <p>No products available.</p>;

  return (
    <div className="space-y-4">
      {/* Toast */}
      {addedMsg && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded shadow-lg z-50">
          {addedMsg}
        </div>
      )}

      <div className="grid grid-cols-3 gap-6">
        {products.map(p => (
          <div
            key={p.id}
            className="border rounded p-4 space-y-2 bg-white shadow-sm"
          >
            <h3 className="font-semibold text-lg">{p.name}</h3>
            <p>Price: ${p.price}</p>
            <p>Stock: {p.stock}</p>

            <button
              disabled={p.stock === 0}
              onClick={() => handleAdd(p)}
              className="btn-primary w-full disabled:opacity-50"
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
