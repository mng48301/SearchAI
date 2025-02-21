import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function QuestionPage() {
  const [query, setQuery] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  useEffect(() => {
    // Pull query from URL
    const params = new URLSearchParams(window.location.search);
    const q = params.get('query');
    if (q) setQuery(q);
  }, []);

  const handleAsk = async () => {
    // Make a request to your AI endpoint with question + context
    // This is just a placeholder
    try {
      const response = await axios.post(`${API_BASE_URL}/ask_context`, {
        originalQuery: query,
        userQuestion: question
      });
      setAnswer(response.data.answer || 'No answer');
    } catch (error) {
      setAnswer('Error asking question');
    }
  };

  return (
    <div className="container my-4">
      <h2>Context-Based Q&A</h2>
      <p>Original query: <strong>{query}</strong></p>
      <div className="mb-3">
        <label>Ask a related question:</label>
        <input
          type="text"
          className="form-control"
          value={question}
          onChange={e => setQuestion(e.target.value)}
        />
      </div>
      <button className="btn btn-custom-primary" onClick={handleAsk}>
        Ask
      </button>
      <div className="mt-3">
        <h4>Answer:</h4>
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default QuestionPage;
