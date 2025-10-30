# 🤖 Career Chatbot API - Complete Usage Guide

## 📡 API Endpoint

**Base URL:** `http://localhost:8002`  
**Endpoint:** `POST /api/chat`  
**Full URL:** `http://localhost:8002/api/chat`

---

## 🔧 How to Use the API

### **Method 1: Using JavaScript/React (Frontend)**

```javascript
// Example React function
async function sendChatMessage(userId, userMessage) {
  const response = await fetch('http://localhost:8002/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,      // ← Your user's UUID from database
      query: userMessage    // ← User's message/question
    })
  });

  const data = await response.json();
  return data;
}

// Usage example
const userId = "550e8400-e29b-41d4-a716-446655440000"; // From your auth system
const userMessage = "I know Python and Machine Learning. Show me jobs";

sendChatMessage(userId, userMessage)
  .then(response => {
    console.log("Intent:", response.intent);
    console.log("Bot Response:", response.response);
    console.log("Skills Extracted:", response.extracted_skills);
    console.log("Jobs:", response.job_recommendations);
  });
```

---

### **Method 2: Using Axios (Frontend)**

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8002';

// Function to send chat message
async function chatWithBot(userId, query) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      user_id: userId,
      query: query
    });
    
    return response.data;
  } catch (error) {
    console.error('Error:', error.response.data);
    throw error;
  }
}

// Example usage
const userId = "550e8400-e29b-41d4-a716-446655440000";
const query = "I know React, JavaScript, and Node.js";

chatWithBot(userId, query)
  .then(data => {
    console.log(data);
  });
```

---

### **Method 3: Using Python (Backend/Testing)**

```python
import requests
import json

# API configuration
API_URL = "http://localhost:8002/api/chat"

# Your data
user_id = "550e8400-e29b-41d4-a716-446655440000"
user_query = "I know Python and TensorFlow. Show me job recommendations"

# Make the request
response = requests.post(
    API_URL,
    json={
        "user_id": user_id,
        "query": user_query
    },
    headers={"Content-Type": "application/json"}
)

# Get the response
if response.status_code == 200:
    data = response.json()
    print("Success!")
    print(f"Intent: {data['intent']}")
    print(f"Response: {data['response']}")
    print(f"Skills: {data['extracted_skills']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

---

### **Method 4: Using cURL (Command Line)**

```bash
curl -X POST "http://localhost:8002/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "I know Python and Machine Learning"
  }'
```

**PowerShell version:**
```powershell
$body = @{
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    query = "I know Python and Machine Learning. Show me jobs"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/api/chat" -Method Post -Body $body -ContentType "application/json"
```

---

## 📥 Request Format

### **Required Fields:**

```json
{
  "user_id": "string (UUID)",     // User's unique ID from your database
  "query": "string"                // User's message/question
}
```

### **Example Requests:**

**Example 1: Adding Skills**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "I know Python, React, and Machine Learning"
}
```

**Example 2: Getting Job Recommendations**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "Show me job recommendations based on my skills"
}
```

**Example 3: Combined (Add Skills + Get Jobs)**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "I know AWS, Docker, Kubernetes. What jobs can I get?"
}
```

---

## 📤 Response Format

### **Success Response (200 OK):**

```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "I know Python and Machine Learning. Show me jobs",
  "intent": "show_jobs",
  "response": "Based on your skills, I found 10 job recommendations for you!",
  "extracted_skills": ["python", "machine learning"],
  "job_recommendations": [
    {
      "job_id": "280159df-5cc4-4b5b-9b46-9f74f3ff53ed",
      "similarity_score": 0.87
    },
    {
      "job_id": "97b4c448-8162-4af3-b4ca-53456b2392e1",
      "similarity_score": 0.85
    }
  ]
}
```

### **Field Explanations:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the request was successful |
| `user_id` | string | The user ID you sent |
| `query` | string | The query you sent |
| `intent` | string | AI-detected intent (add_skills, show_jobs, etc.) |
| `response` | string | **Main chatbot response text to show to user** |
| `extracted_skills` | array | Skills extracted from the query (can be null) |
| `job_recommendations` | array | Job recommendations if intent is "show_jobs" (can be null) |

---

## 🎯 What Happens Behind the Scenes

### **Step 1: You Send Request**
```
POST http://localhost:8002/api/chat
Body: { user_id: "xxx", query: "I know Python" }
```

### **Step 2: AI Analyzes Query**
- **Intent Classification:** Determines what user wants (add skills, show jobs, etc.)
- **Skill Extraction:** Finds skills mentioned (Python, React, AWS, etc.)

### **Step 3: Database Update (if skills found)**
- Extracts skills from query
- Fetches existing skills from database
- Merges new + existing skills
- Updates `users` table `skills` column

### **Step 4: Call Recommendation API (if needed)**
- If intent is "show_jobs"
- Calls `http://localhost:8000/api/recommend`
- Gets job recommendations based on updated skills

### **Step 5: Return Response**
- Generates intelligent response text
- Includes extracted skills
- Includes job recommendations (if applicable)

---

## 🎨 Complete React Component Example

```javascript
import React, { useState } from 'react';

function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Replace with actual user ID from your auth context
  const userId = "550e8400-e29b-41d4-a716-446655440000";

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { type: 'user', text: input };
    setMessages([...messages, userMessage]);
    setLoading(true);

    try {
      // Call API
      const response = await fetch('http://localhost:8002/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          query: input
        })
      });

      const data = await response.json();

      // Add bot response to chat
      const botMessage = {
        type: 'bot',
        text: data.response,
        skills: data.extracted_skills,
        jobs: data.job_recommendations
      };

      setMessages([...messages, userMessage, botMessage]);
      setInput('');
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        type: 'bot',
        text: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages([...messages, userMessage, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            <p>{msg.text}</p>
            
            {/* Show extracted skills */}
            {msg.skills && (
              <div className="skills">
                <strong>Skills added:</strong> {msg.skills.join(', ')}
              </div>
            )}
            
            {/* Show job recommendations */}
            {msg.jobs && (
              <div className="jobs">
                <strong>Found {msg.jobs.length} jobs!</strong>
                {msg.jobs.slice(0, 3).map(job => (
                  <div key={job.job_id}>
                    Job ID: {job.job_id} (Score: {job.similarity_score.toFixed(2)})
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default ChatBot;
```

---

## 💡 Example Conversations

### **Conversation 1: Adding Skills**
```
User: "I know Python, JavaScript, and React"
Bot: "Great! I've added the following skills to your profile: 
      python, javascript, react. You can now get personalized 
      job recommendations based on your skills!"
```

### **Conversation 2: Getting Jobs**
```
User: "Show me job recommendations"
Bot: "Based on your skills, I found 10 job recommendations 
      for you! Check out the job_recommendations field for details."
(Returns job IDs and similarity scores)
```

### **Conversation 3: Combined**
```
User: "I also learned AWS and Docker. What jobs can I get?"
Bot: "Great! I've added the following skills to your profile: 
      aws, docker. Based on your skills, I found 10 job 
      recommendations for you!"
(Updates skills + returns jobs)
```

---

## 🔐 Where to Get user_id

The `user_id` comes from your authentication system:

### **Option 1: After User Login**
```javascript
// After successful login
localStorage.setItem('user_id', response.user_id);

// Later, when calling chatbot
const userId = localStorage.getItem('user_id');
```

### **Option 2: From Auth Context (React)**
```javascript
import { useAuth } from './AuthContext';

function ChatBot() {
  const { user } = useAuth(); // Get from your auth context
  const userId = user.id;
  
  // Use userId in API calls
}
```

### **Option 3: From Database Session**
```javascript
// If you have a session endpoint
const response = await fetch('/api/session');
const { user_id } = await response.json();
```

---

## ⚠️ Important Notes

1. **Make sure the server is running:**
   ```powershell
   python -m uvicorn chatbot_api:app --host 0.0.0.0 --port 8002
   ```

2. **User must exist in database:**
   - The `user_id` must exist in the `users` table
   - Otherwise you'll get a 404 error

3. **CORS for Production:**
   - Update `ALLOWED_ORIGINS` in the code
   - Don't use `*` in production

4. **Skills are auto-extracted:**
   - No need to format skills specially
   - Just write naturally: "I know Python and React"
   - AI will extract: `["python", "react"]`

5. **Database auto-updates:**
   - Skills are automatically added to database
   - Merges with existing skills
   - No duplicates

---

## 🐛 Testing the API

Use the provided test script:
```powershell
python test_chatbot_api.py
```

Or test manually:
```powershell
$body = @{
    user_id = "YOUR-ACTUAL-USER-ID"
    query = "I know Python and Machine Learning"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/api/chat" -Method Post -Body $body -ContentType "application/json"
```

---

## 📊 Response Flow Diagram

```
User Types Message
        ↓
Frontend sends: { user_id, query }
        ↓
API receives request
        ↓
AI analyzes intent + extracts skills
        ↓
Updates database (if skills found)
        ↓
Calls job API (if user wants jobs)
        ↓
Generates response text
        ↓
Returns: { response, intent, skills, jobs }
        ↓
Frontend displays response to user
```

---

## ✅ Summary

**To use the API, you need:**
1. ✅ User ID (UUID from your users table)
2. ✅ User's query/message (natural language)
3. ✅ POST request to `http://localhost:8002/api/chat`
4. ✅ Display the `response` field to user
5. ✅ Optionally show `extracted_skills` and `job_recommendations`

That's it! The API handles everything else automatically.
