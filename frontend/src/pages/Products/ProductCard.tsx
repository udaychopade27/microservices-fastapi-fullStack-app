import { useCart } from '../../hooks/useCart';

export default function ProductCard({ product }: any) {
  const { add } = useCart();

  return (
    <div className="border rounded p-4">
      <h3 className="font-semibold">{product.name}</h3>
      <p>${product.price}</p>

      <button
        onClick={() =>
          add({
            id: product.id,
            name: product.name,
            price: product.price
          })
        }
        className="btn-primary mt-2"
      >
        Add to Cart
      </button>
    </div>
  );
}
