// React Component Example for Job Recommendations
// File: JobRecommendations.jsx

import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const JobRecommendations = () => {
  const [skills, setSkills] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState(null);

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setApiHealth(data);
    } catch (err) {
      console.error('API health check failed:', err);
    }
  };

  const getRecommendations = async () => {
    if (!skills.trim()) {
      setError('Please enter at least one skill');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Split skills by comma or space
      const skillsArray = skills
        .split(/[,\s]+/)
        .filter(skill => skill.trim() !== '');

      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skills: skillsArray,
          top_n: 10
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      getRecommendations();
    }
  };

  return (
    <div className="job-recommendations-container" style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>AI Job Recommendation System</h1>
      
      {/* API Health Status */}
      {apiHealth && (
        <div style={{ 
          padding: '10px', 
          marginBottom: '20px', 
          backgroundColor: apiHealth.model_loaded ? '#d4edda' : '#f8d7da',
          borderRadius: '5px'
        }}>
          <strong>API Status:</strong> {apiHealth.status} | 
          <strong> Model Loaded:</strong> {apiHealth.model_loaded ? '✓' : '✗'} | 
          <strong> Jobs Cached:</strong> {apiHealth.total_jobs}
        </div>
      )}

      {/* Search Input */}
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter your skills (e.g., python, machine learning, react)"
          style={{
            width: '70%',
            padding: '12px',
            fontSize: '16px',
            borderRadius: '5px',
            border: '1px solid #ccc'
          }}
        />
        <button
          onClick={getRecommendations}
          disabled={loading}
          style={{
            width: '28%',
            marginLeft: '2%',
            padding: '12px',
            fontSize: '16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      {/* Recommendations List */}
      {recommendations.length > 0 && (
        <div>
          <h2>Top {recommendations.length} Job Recommendations</h2>
          <div style={{ display: 'grid', gap: '20px' }}>
            {recommendations.map((job, index) => (
              <div
                key={index}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '20px',
                  backgroundColor: '#f9f9f9',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 10px 0', color: '#007bff' }}>
                      {index + 1}. {job.job_role}
                    </h3>
                    <p style={{ margin: '5px 0', color: '#666' }}>
                      <strong>Company:</strong> {job.company}
                    </p>
                    <p style={{ margin: '5px 0', color: '#666' }}>
                      <strong>Category:</strong> {job.category}
                    </p>
                    <p style={{ margin: '10px 0', fontSize: '14px' }}>
                      <strong>Required Skills:</strong> {job.required_skills}
                    </p>
                    <p style={{ margin: '10px 0', fontSize: '14px', color: '#555' }}>
                      {job.job_description.substring(0, 200)}...
                    </p>
                  </div>
                  <div style={{
                    marginLeft: '20px',
                    textAlign: 'center',
                    minWidth: '100px'
                  }}>
                    <div style={{
                      fontSize: '24px',
                      fontWeight: 'bold',
                      color: job.similarity_score > 0.7 ? '#28a745' : 
                             job.similarity_score > 0.5 ? '#ffc107' : '#6c757d'
                    }}>
                      {(job.similarity_score * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Match</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {!loading && recommendations.length === 0 && skills && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: '#666'
        }}>
          No recommendations found. Try different skills.
        </div>
      )}
    </div>
  );
};

export default JobRecommendations;


// ============================================
// Alternative: Using Custom Hook
// ============================================

// File: useJobRecommendations.js
export const useJobRecommendations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRecommendations = async (skills, topN = 10) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skills: Array.isArray(skills) ? skills : [skills],
          top_n: topN
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch recommendations');
      }

      const data = await response.json();
      return data.recommendations;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { getRecommendations, loading, error };
};


// ============================================
// Usage Example with the Custom Hook
// ============================================

/*
import { useJobRecommendations } from './useJobRecommendations';

function MyComponent() {
  const { getRecommendations, loading, error } = useJobRecommendations();
  const [recommendations, setRecommendations] = useState([]);

  const handleSearch = async () => {
    const skills = ['python', 'machine learning', 'data science'];
    const results = await getRecommendations(skills, 10);
    setRecommendations(results);
  };

  return (
    <div>
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Loading...' : 'Search Jobs'}
      </button>
      {error && <div>Error: {error}</div>}
      {recommendations.map(job => (
        <div key={job.job_id}>{job.job_role}</div>
      ))}
    </div>
  );
}
*/
