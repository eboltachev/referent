import { useState } from 'react';

type Props = { jobId: string };

export default function QuestionPanel({ jobId }: Props) {
  const [question, setQuestion] = useState('');
  const [output, setOutput] = useState('');

  async function ask() {
    setOutput('');
    const response = await fetch(`/api/jobs/${jobId}/questions/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    if (!response.body) return;
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      setOutput((current) => current + decoder.decode(value));
    }
  }

  return (
    <div>
      <input
        className="question"
        placeholder="Вопрос"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') void ask();
        }}
      />
      <button onClick={() => void ask()}>Спросить</button>
      <pre>{output}</pre>
    </div>
  );
}
