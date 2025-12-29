export default function ErrorState({ message }: { message: string }) {
  return <div className="text-red-600">{message}</div>;
}
