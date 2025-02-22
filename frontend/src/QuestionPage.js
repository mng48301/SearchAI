import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart } from 'react-google-charts';
import ReactMarkdown from 'react-markdown';
import './QuestionPage.css';

const API_BASE_URL = 'http://localhost:8000';

function QuestionPage() {
  const [query, setQuery] = useState('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('query');
    if (q) setQuery(q);
  }, []);

  const handleAsk = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/ask_context`, {
        originalQuery: query,
        userQuestion: question
      });

      const result = response.data;
      setResponse(result);
      setLoading(false);
    } catch (error) {
      console.error('Error asking question:', error);
      setLoading(false);
    }
  };

  const renderResponse = (response) => {
    if (!response) return null;

    switch (response.type) {
      case 'graph':
        return (
          <div className="response-container graph">
            <h4>{response.title}</h4>
            <Chart
              chartType={response.graphType}
              data={response.data}
              options={response.options}
              width="100%"
              height="400px"
            />
          </div>
        );

      case 'table':
        return (
          <div className="response-container table">
            <h4>{response.title}</h4>
            <table className="data-table">
              <thead>
                <tr>
                  {response.headers.map((header, i) => (
                    <th key={i}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {response.data.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      case 'markdown':
        return (
          <div className="response-container markdown">
            <ReactMarkdown>{response.content}</ReactMarkdown>
          </div>
        );

      default:
        return (
          <div className="response-container text">
            <div className="content">
              {response.content || "No response available. Please try rephrasing your question."}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="question-page container my-4">
      <header className="page-header white-important-text">
        <h2>Context-Based Analysis</h2>
        <p className="original-query">Original search: <strong>{query}</strong></p>
      </header>

      <div className="question-section card shadow-lg">
        <div className="card-body">
          <div className="input-group mb-3">
            <input
              type="text"
              className="form-control"
              placeholder="Ask a question about the search results..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <button 
              className="btn btn-custom-primary"
              onClick={handleAsk}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Ask'}
            </button>
          </div>
          <div className="helper-text white-important-text">
            Try asking about:
            <ul>
              <li>Price comparisons or trends</li>
              <li>Statistical analysis</li>
              <li>Data visualization requests</li>
              <li>Detailed summaries</li>
            </ul>
          </div>
        </div>
      </div>

      {response && (
        <div className="response-section mt-4">
          {renderResponse(response)}
        </div>
      )}

      <div className="navigation-buttons mt-4">
        <button 
          className="btn btn-secondary"
          onClick={() => window.location.href = '/'}
        >
          <i className="material-icons" style={{fontSize: '16px', marginRight: '4px'}}>
            arrow_back
          </i>
          Back to Search
        </button>
      </div>
    </div>
  );
}

export default QuestionPage;