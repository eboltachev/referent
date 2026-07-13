type Props = { onCancel: () => void };

export default function CancelButton({ onCancel }: Props) {
  return <button className="cancel" onClick={onCancel}>Отмена</button>;
}
