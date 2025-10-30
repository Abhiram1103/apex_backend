# 🎨 Frontend Integration Guide - Complete React Examples

## 📋 Overview

This guide shows you exactly how to integrate all 3 APIs into your React/Next.js frontend.

---

## 🔧 Setup

### 1. Install Dependencies

```bash
npm install axios
# or
yarn add axios
```

### 2. Create Environment Variables

Create `.env.local` in your frontend root:

```env
NEXT_PUBLIC_JOB_API_URL=https://job-recommendation-api.onrender.com
NEXT_PUBLIC_SKILL_GAP_API_URL=https://skill-gap-api.onrender.com
NEXT_PUBLIC_CHATBOT_API_URL=https://chatbot-api.onrender.com
```

---

## 📁 Project Structure

```
frontend/
├── services/
│   ├── jobAPI.js
│   ├── skillGapAPI.js
│   └── chatbotAPI.js
├── components/
│   ├── JobRecommendations.jsx
│   ├── SkillGapAnalysis.jsx
│   └── ChatInterface.jsx
└── .env.local
```

---

## 🔌 API Service Files

### `services/jobAPI.js`

```javascript
import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_JOB_API_URL;

const jobAPI = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Get job recommendations
export const getJobRecommendations = async (userId, topN = 10) => {
  try {
    const { data } = await jobAPI.post('/api/recommend', {
      user_id: userId,
      top_n: topN,
    });
    return data;
  } catch (error) {
    console.error('Job API Error:', error.response?.data || error.message);
    throw error;
  }
};

// Check API health
export const checkJobAPIHealth = async () => {
  try {
    const { data } = await jobAPI.get('/health');
    return data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default jobAPI;
```

### `services/skillGapAPI.js`

```javascript
import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_SKILL_GAP_API_URL;

const skillGapAPI = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Get skill gap analysis
export const getSkillGapAnalysis = async (userId, topN = 10) => {
  try {
    const { data } = await skillGapAPI.post('/api/skill-gap', {
      user_id: userId,
      top_n: topN,
    });
    return data;
  } catch (error) {
    console.error('Skill Gap API Error:', error.response?.data || error.message);
    throw error;
  }
};

// Check API health
export const checkSkillGapAPIHealth = async () => {
  try {
    const { data } = await skillGapAPI.get('/health');
    return data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default skillGapAPI;
```

### `services/chatbotAPI.js`

```javascript
import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL;

const chatbotAPI = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Send chat message
export const sendChatMessage = async (userId, query) => {
  try {
    const { data } = await chatbotAPI.post('/api/chat', {
      user_id: userId,
      query: query,
    });
    return data;
  } catch (error) {
    console.error('Chatbot API Error:', error.response?.data || error.message);
    throw error;
  }
};

// Check API health
export const checkChatbotAPIHealth = async () => {
  try {
    const { data } = await chatbotAPI.get('/health');
    return data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default chatbotAPI;
```

---

## 🎨 React Components

### 1. Job Recommendations Component

`components/JobRecommendations.jsx`

```javascript
import { useState, useEffect } from 'react';
import { getJobRecommendations } from '../services/jobAPI';

export default function JobRecommendations({ userId }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecommendations();
  }, [userId]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getJobRecommendations(userId, 10);
      setRecommendations(data.recommendations);
    } catch (err) {
      setError('Failed to load recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchRecommendations}
          className="mt-2 text-red-600 hover:text-red-800 font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">
        Job Recommendations for You
      </h2>

      {recommendations.length === 0 ? (
        <p className="text-gray-500">No recommendations available yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.map((job) => (
            <div
              key={job.job_id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-500">
                  Job ID: {job.job_id.substring(0, 8)}...
                </span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-bold ${
                    job.similarity_score > 0.8
                      ? 'bg-green-100 text-green-800'
                      : job.similarity_score > 0.6
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {(job.similarity_score * 100).toFixed(1)}% Match
                </span>
              </div>

              <div className="mt-4">
                <button
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  onClick={() => {
                    /* Navigate to job details */
                  }}
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={fetchRecommendations}
        className="mt-4 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
      >
        Refresh Recommendations
      </button>
    </div>
  );
}
```

### 2. Skill Gap Analysis Component

`components/SkillGapAnalysis.jsx`

```javascript
import { useState, useEffect } from 'react';
import { getSkillGapAnalysis } from '../services/skillGapAPI';

export default function SkillGapAnalysis({ userId }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalysis();
  }, [userId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getSkillGapAnalysis(userId, 10);
      setAnalysis(data);
    } catch (err) {
      setError('Failed to load skill gap analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchAnalysis}
          className="mt-2 text-red-600 hover:text-red-800 font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!analysis) {
    return <p className="text-gray-500">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Skill Gap Analysis
        </h2>
        <p className="text-gray-600">
          Your current skills: {analysis.user_skills.join(', ')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {analysis.top_opportunities.map((opportunity) => (
          <div
            key={opportunity.job_id}
            className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {opportunity.job_role}
                </h3>
                <p className="text-sm text-gray-600">{opportunity.company}</p>
              </div>
              <span className="text-2xl font-bold text-green-600">
                ₹{(opportunity.avg_salary / 100000).toFixed(1)}L
              </span>
            </div>

            <div className="space-y-3">
              {/* Similarity Score */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Skill Match</span>
                  <span className="font-medium">
                    {(opportunity.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width: `${opportunity.similarity_score * 100}%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Combined Score */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Overall Score</span>
                  <span className="font-medium">
                    {(opportunity.combined_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full"
                    style={{
                      width: `${opportunity.combined_score * 100}%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Matching Skills */}
              {opportunity.matching_skills.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    ✅ Your Matching Skills:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.matching_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Skills */}
              {opportunity.missing_skills.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    📚 Skills to Learn:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.missing_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Salary Range */}
              <div className="pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Salary Range: ₹{(opportunity.min_salary / 100000).toFixed(1)}L
                  - ₹{(opportunity.max_salary / 100000).toFixed(1)}L
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={fetchAnalysis}
        className="mt-4 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
      >
        Refresh Analysis
      </button>
    </div>
  );
}
```

### 3. AI Chatbot Component

`components/ChatInterface.jsx`

```javascript
import { useState, useEffect, useRef } from 'react';
import { sendChatMessage } from '../services/chatbotAPI';

export default function ChatInterface({ userId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(userId, input);

      const botMessage = {
        role: 'assistant',
        content: response.response,
        intent: response.intent,
        extracted_skills: response.extracted_skills,
        job_recommendations: response.job_recommendations,
        skill_gap_analysis: response.skill_gap_analysis,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        error: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <h3 className="text-lg font-semibold">AI Career Assistant</h3>
        <p className="text-sm opacity-90">
          Ask me about jobs, skills, or career advice!
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="mb-4">👋 Hi! I'm your AI career assistant.</p>
            <p className="text-sm">You can ask me to:</p>
            <ul className="text-sm mt-2 space-y-1">
              <li>• Show job recommendations</li>
              <li>• Analyze skill gaps</li>
              <li>• Check salary information</li>
              <li>• Add new skills</li>
              <li>• Give career advice</li>
            </ul>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.error
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>

              {/* Show intent badge */}
              {msg.intent && (
                <span className="inline-block mt-2 px-2 py-1 bg-white bg-opacity-20 rounded text-xs">
                  Intent: {msg.intent}
                </span>
              )}

              {/* Show extracted skills */}
              {msg.extracted_skills && msg.extracted_skills.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium mb-1">Extracted Skills:</p>
                  <div className="flex flex-wrap gap-1">
                    {msg.extracted_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 bg-white bg-opacity-20 rounded text-xs"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Show job recommendations count */}
              {msg.job_recommendations && msg.job_recommendations.length > 0 && (
                <p className="mt-2 text-xs opacity-75">
                  📊 {msg.job_recommendations.length} jobs recommended
                </p>
              )}

              {/* Show skill gap analysis indicator */}
              {msg.skill_gap_analysis &&
                msg.skill_gap_analysis.top_opportunities && (
                  <p className="mt-2 text-xs opacity-75">
                    📈{' '}
                    {msg.skill_gap_analysis.top_opportunities.length}{' '}
                    opportunities analyzed
                  </p>
                )}

              <p className="text-xs opacity-50 mt-1">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0.1s' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows="2"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>

        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
```

---

## 🎯 Usage in Pages

### Main Dashboard Page

`pages/dashboard.jsx` or `app/dashboard/page.jsx`

```javascript
import { useState } from 'react';
import JobRecommendations from '../components/JobRecommendations';
import SkillGapAnalysis from '../components/SkillGapAnalysis';
import ChatInterface from '../components/ChatInterface';

export default function Dashboard() {
  const [userId] = useState('user123'); // Get from auth context
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Career Dashboard
        </h1>

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          {['chat', 'jobs', 'skills'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-2 px-4 font-medium transition-colors ${
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab === 'chat' && '💬 AI Chat'}
              {tab === 'jobs' && '🎯 Job Recommendations'}
              {tab === 'skills' && '📊 Skill Gap Analysis'}
            </button>
          ))}
        </div>

        {/* Content */}
        <div>
          {activeTab === 'chat' && <ChatInterface userId={userId} />}
          {activeTab === 'jobs' && <JobRecommendations userId={userId} />}
          {activeTab === 'skills' && <SkillGapAnalysis userId={userId} />}
        </div>
      </div>
    </div>
  );
}
```

---

## 🧪 Testing Component

Create a test component to verify all APIs work:

`components/APIHealthCheck.jsx`

```javascript
import { useState } from 'react';
import {
  checkJobAPIHealth,
  checkSkillGapAPIHealth,
  checkChatbotAPIHealth,
} from '../services/';

export default function APIHealthCheck() {
  const [status, setStatus] = useState({
    job: null,
    skillGap: null,
    chatbot: null,
  });

  const checkAllAPIs = async () => {
    // Check Job API
    try {
      const jobHealth = await checkJobAPIHealth();
      setStatus((prev) => ({ ...prev, job: jobHealth }));
    } catch (error) {
      setStatus((prev) => ({ ...prev, job: { error: true } }));
    }

    // Check Skill Gap API
    try {
      const skillGapHealth = await checkSkillGapAPIHealth();
      setStatus((prev) => ({ ...prev, skillGap: skillGapHealth }));
    } catch (error) {
      setStatus((prev) => ({ ...prev, skillGap: { error: true } }));
    }

    // Check Chatbot API
    try {
      const chatbotHealth = await checkChatbotAPIHealth();
      setStatus((prev) => ({ ...prev, chatbot: chatbotHealth }));
    } catch (error) {
      setStatus((prev) => ({ ...prev, chatbot: { error: true } }));
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">API Health Check</h3>

      <div className="space-y-2">
        {Object.entries(status).map(([api, health]) => (
          <div key={api} className="flex items-center justify-between">
            <span className="capitalize">{api} API:</span>
            <span
              className={`px-3 py-1 rounded ${
                health?.status === 'healthy'
                  ? 'bg-green-100 text-green-800'
                  : health?.error
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {health?.status || health?.error ? 'Error' : 'Not Checked'}
            </span>
          </div>
        ))}
      </div>

      <button
        onClick={checkAllAPIs}
        className="mt-4 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        Check All APIs
      </button>
    </div>
  );
}
```

---

## ✅ Final Checklist

- [ ] All service files created
- [ ] Environment variables configured
- [ ] All components working locally
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] Tested with real API URLs
- [ ] CORS working (no console errors)
- [ ] Mobile responsive design
- [ ] Deployed to Vercel

---

## 📞 Need Help?

Check:
1. Browser console for errors
2. Network tab for API calls
3. Environment variables are correct
4. APIs are deployed and running

Your frontend is now fully integrated with all 3 backend APIs! 🎉
