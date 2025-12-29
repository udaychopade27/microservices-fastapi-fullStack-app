import { useEffect, useState } from 'react';
import { apiFetch } from '../../api/client';
import { Product } from '../../types';

export default function Inventory() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Add product form
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await apiFetch<Product[]>('/api/products');
      setProducts(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  // ADD PRODUCT
  const addProduct = async () => {
    try {
      await apiFetch('/api/products', {
        method: 'POST',
        body: JSON.stringify({
          name,
          price: Number(price),
          stock: Number(quantity),
        }),
      });

      setName('');
      setPrice('');
      setQuantity('');
      loadProducts();
    } catch (e: any) {
      setError(e.message);
    }
  };

  // UPDATE PRICE
  const updatePrice = async (id: string, price: number) => {
    try {
      await apiFetch(`/api/products/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ price }),
      });
      loadProducts();
    } catch (e: any) {
      setError(e.message);
    }
  };

  // REFILL STOCK (⚠️ qty, not amount)
  const refillStock = async (id: string, qty: number) => {
    try {
      await apiFetch(`/api/refill/${id}`, {
        method: 'POST',
        body: JSON.stringify({ qty }),
      });
      loadProducts();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-8">
      <h2 className="text-xl font-semibold">Inventory Manager</h2>

      {error && <p className="text-red-600">{error}</p>}
      {loading && <p>Loading inventory…</p>}

      {/* ADD PRODUCT */}
      <div className="border rounded p-4 space-y-4 max-w-md">
        <h3 className="font-medium">Add New Product</h3>

        <div>
          <label className="block text-sm font-medium">Product Name</label>
          <input
            className="input"
            value={name}
            onChange={e => setName(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Price</label>
          <input
            className="input"
            type="number"
            value={price}
            onChange={e => setPrice(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Initial Quantity</label>
          <input
            className="input"
            type="number"
            value={quantity}
            onChange={e => setQuantity(e.target.value)}
          />
        </div>

        <button className="btn-primary w-full" onClick={addProduct}>
          Add Product
        </button>
      </div>

      {/* PRODUCT LIST */}
      <div className="space-y-4">
        {products.map(p => (
          <div
            key={p.id}
            className="border rounded p-4 grid grid-cols-5 gap-4 items-center"
          >
            <strong>{p.name}</strong>

            <div>
              <label className="block text-xs">Price</label>
              <input
                className="input"
                type="number"
                defaultValue={p.price}
                onBlur={e =>
                  updatePrice(p.id, Number(e.target.value))
                }
              />
            </div>

            <div>
              <label className="block text-xs">Stock</label>
              <span>{p.stock}</span>
            </div>

            <div>
              <label className="block text-xs">Refill Quantity</label>
              <input
                className="input"
                type="number"
                placeholder="Enter qty & press Enter"
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    refillStock(
                      p.id,
                      Number((e.target as HTMLInputElement).value)
                    );
                    (e.target as HTMLInputElement).value = '';
                  }
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
