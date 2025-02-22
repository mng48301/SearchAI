import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Routes, Route } from 'react-router-dom';
import QuestionPage from './QuestionPage';

// Add API base URL
const API_BASE_URL = 'http://localhost:8000';

function MainApp() {
  const [scrapedData, setScrapedData] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [activeSearches, setActiveSearches] = useState([]);
  const [sourceDetail, setSourceDetail] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      console.log('Fetching data from:', `${API_BASE_URL}/data/`);
      const response = await axios.get(`${API_BASE_URL}/data/`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response:', response);
      
      if (response.data.error) {
        throw new Error(response.data.error);
      }
      
      setScrapedData(response.data.data || []);
    } catch (error) {
      console.error('Detailed error:', error);
      console.error('Error response:', error.response);
      setScrapedData([]);
      // Show a more user-friendly error message
      alert(`Error: ${error.response?.data?.error || error.message || 'Could not fetch data'}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!searchQuery) return;
    
    const searchId = Date.now().toString();
    setActiveSearches(prev => [...prev, {
      id: searchId,
      query: searchQuery,
      status: 'Processing',
      progress: 0
    }]);

    // Add polling for progress updates
    const progressInterval = setInterval(async () => {
      try {
        const statusResponse = await axios.get(`${API_BASE_URL}/search/${searchId}/status`);
        const { status, progress } = statusResponse.data;
        
        setActiveSearches(prev => 
          prev.map(search => 
            search.id === searchId
              ? { ...search, status, progress: progress || 0 }
              : search
          )
        );

        if (status === 'completed' || status === 'failed' || status === 'cancelled') {
          clearInterval(progressInterval);
          if (status === 'completed') fetchData();
        }
      } catch (error) {
        console.error('Error checking progress:', error);
      }
    }, 1000);

    try {
      const response = await axios.get(`${API_BASE_URL}/search/`, { 
        params: { query: searchQuery }
      });
      
      if (response.data.status === 'cancelled') {
        // Search was cancelled, remove it from active searches
        setActiveSearches(prev => 
          prev.filter(search => search.id !== searchId)
        );
        return;
      }
      
      console.log('Search response:', response.data);
      
      if (response.data.status === 'completed') {
        // Success case
        setActiveSearches(prev => 
          prev.map(search => 
            search.id === searchId
              ? { ...search, status: 'Completed', progress: 100 }
              : search
          )
        );
        fetchData();
      } else {
        // Error case
        setActiveSearches(prev => 
          prev.map(search => 
            search.id === searchId
              ? { ...search, status: 'Failed', progress: 0 }
              : search
          )
        );
        alert(response.data.error || 'Search failed');
      }
      
      setSearchQuery('');
    } catch (error) {
      console.error('Search error:', error);
      setActiveSearches(prev => 
        prev.map(search => 
          search.id === searchId
            ? { ...search, status: 'Failed', progress: 0 }
            : search
        )
      );
    }
  };

  const fetchSourceDetail = async (url) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/source_detail`, { 
        params: { url }
      });
      setSourceDetail(response.data.content || 'No content found');
      alert(`Full Content:\n\n${response.data.content || 'No content found'}`);
    } catch (error) {
      console.error('Error fetching source detail:', error);
      alert('Could not fetch source detail');
    }
  };

  const cancelSearch = async (searchId) => {
    try {
      // Update UI instantly to show cancel state
      setActiveSearches(prev => 
        prev.map(search => 
          search.id === searchId
            ? { ...search, status: 'Cancelling...', progress: 0 }
            : search
        )
      );

      await axios.post(`${API_BASE_URL}/cancel/${searchId}`);
      
      setTimeout(() => {
        setActiveSearches(prev => 
          prev.filter(search => search.id !== searchId)
        );
      }, 1000);
      
    } catch (error) {
      console.error('Error cancelling search:', error);
      // Revert to previous state if cancellation fails
      setActiveSearches(prev => 
        prev.map(search => 
          search.id === searchId
            ? { ...search, status: 'Processing' }
            : search
        )
      );
    }
  };

  const handleDelete = async (query) => {
    if (window.confirm(`Are you sure you want to delete search results for: ${query}?`)) {
      try {
        await axios.delete(`${API_BASE_URL}/search/${encodeURIComponent(query)}`);
        // Refresh the data
        fetchData();
      } catch (error) {
        console.error('Error deleting search:', error);
        alert('Failed to delete search');
      }
    }
  };

  function truncate(text = '', maxLength = 50) {
    return text.length <= maxLength ? text : text.slice(0, maxLength) + '...';
  }

  return (
    <div className="container my-4">
      <header className="app-header text-center">
        <h1>SearchAI</h1>
        <p className="mt-2 mb-0">Intelligent Web Search Platform</p>
      </header>

      <section className="mb-5">
        <div className="card shadow-lg">
          <div className="card-header">
            <h5 className="mb-0">New Search</h5>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit} className="d-flex gap-3">
              <input
                type="text"
                className="form-control"
                placeholder="Enter search query..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                disabled={isSearching}
              />
              <button 
                type="submit" 
                className="btn btn-custom-primary"
                disabled={isSearching}
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </form>
          </div>
        </div>
      </section>

      <section className="mb-4">
        <h2 className="mb-3 text-white-important">Active Searches</h2>
        <div className="row">
          {activeSearches.map((search) => (
            <div key={search.id} className="col-md-6 mb-3">
              <div className="card h-100 shadow-sm">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <h5 className="card-title">
                        <span className="search-query text-white-important" title={search.query}>
                          {search.query}
                        </span>
                      </h5>
                      <div className="task-info text-dullwhite-important">
                        <strong>Status:</strong> {search.status}
                      </div>
                    </div>
                    {search.status === 'Processing' && (
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => cancelSearch(search.id)}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                  {search.status === 'Processing' && (
                    <div className="progress mt-2" style={{ height: '20px' }}>
                      <div
                        className="progress-bar progress-bar-striped progress-bar-animated bg-warning"
                        role="progressbar"
                        style={{ width: `${search.progress}%` }}
                        aria-valuenow={search.progress}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      >
                        {search.progress}%
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-white-important">Search Results</h2>
        {scrapedData.length > 0 ? (
          <table className="table table-hover table-bordered shadow-sm text-dullwhite-important">
            <thead className="table-dark">
              <tr>
                <th>Query</th>
                <th>Top Sites</th>
                <th>Summary</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              {scrapedData.map((item, index) => (
                <tr key={index}>
                  <td>{item.query || 'N/A'}</td>
                  <td>
                    {item.sites?.slice(0, 3).map((site, i) => (
                      <div key={i}>
                        <a
                          href={site}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ marginRight: '10px' }}
                        >
                          {truncate(site, 30)}
                        </a>
                      </div>
                    ))}
                  </td>
                  <td>{truncate(item.summary || 'No summary', 80)}</td>
                  <td className="options-cell">
                    <div className="btn-action-group">
                      <button
                        className="btn btn-analyze"
                        onClick={() => {
                          window.location.href = `/analyze?query=${encodeURIComponent(item.query)}`;
                        }}
                      >
                        <i className="material-icons" style={{fontSize: '16px', marginRight: '4px'}}>
                          analytics
                        </i>
                        Analyze
                      </button>
                      <button
                        className="btn btn-delete"
                        onClick={() => handleDelete(item.query)}
                      >
                        <i className="material-icons" style={{fontSize: '16px', marginRight: '4px'}}>
                          delete
                        </i>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No search results found.</p>
        )}
      </section>
    </div>
  );
}

// use default export instead of router setup
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainApp />} />
      <Route path="/analyze" element={<QuestionPage />} />
    </Routes>
  );
}
