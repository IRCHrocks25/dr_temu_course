# AI Chatbot API Payloads Documentation

## Overview
This document describes the payload structures for the AI Chatbot feature, including training and interaction endpoints.

---

## 1. Training Webhook Payload

### Endpoint
**POST** `https://katalyst-crm2.fly.dev/webhook/425e8e67-2aa6-4c50-b67f-0162e2496b51`

### Purpose
Sends the lesson transcript to train the AI chatbot for a specific lesson.

### Request Payload

```json
{
  "transcript": "Full lesson transcript text here...",
  "lesson_id": 11,
  "lesson_title": "Introduction to Time Management",
  "course_name": "Time Management Mastery",
  "lesson_slug": "introduction-to-time-management"
}
```

### Payload Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transcript` | string | Yes | The complete lesson transcript text that the AI will learn from |
| `lesson_id` | integer | Yes | Unique identifier for the lesson in the database |
| `lesson_title` | string | Yes | The title of the lesson |
| `course_name` | string | Yes | The name of the course this lesson belongs to |
| `lesson_slug` | string | Yes | URL-friendly identifier for the lesson |

### Example Request

```json
{
  "transcript": "03:27 and have more time off. That's completely up to you and will be in completely in your hands, but using these strategies, you will allow yourself a little more freedom. You can feel proud of the effort and the progress you're making whilst continuing to produce these results and reaching your goals. 03:47 So we're gonna dive right in with the first technique from Brian Tracy in the next video. Welcome to Time Management Mastery. And again, thank you for being a part of the Line Training community. See you in the next lesson.",
  "lesson_id": 11,
  "lesson_title": "Introduction to Time Management",
  "course_name": "Time Management Mastery",
  "lesson_slug": "introduction-to-time-management"
}
```

### Expected Response

#### Success Response (200 OK)

```json
{
  "success": true,
  "chatbot_webhook_id": "d39397da-cf2c-4282-b531-51a321af8586",
  "message": "Training completed successfully"
}
```

**OR**

```json
{
  "webhook_id": "d39397da-cf2c-4282-b531-51a321af8586",
  "status": "trained"
}
```

**OR**

```json
{
  "id": "d39397da-cf2c-4282-b531-51a321af8586"
}
```

**Note:** The webhook may return the chatbot webhook ID in different field names:
- `chatbot_webhook_id`
- `webhook_id`
- `id`

The system will check all three fields and store whichever one is present.

#### Error Response (Non-200 Status)

```json
{
  "error": "Error message describing what went wrong",
  "status": "failed"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `chatbot_webhook_id` / `webhook_id` / `id` | string | Unique identifier for the trained chatbot (optional, may be returned) |
| `success` | boolean | Indicates if training was successful |
| `message` | string | Human-readable status message |
| `error` | string | Error message if training failed |

---

## 2. Chatbot Interaction Payload

### Endpoint
**POST** `/api/lessons/{lesson_id}/chatbot/`

### Purpose
Sends a user's question to the trained AI chatbot and receives a response.

### Request Payload

```json
{
  "message": "What are the key strategies mentioned in this lesson?"
}
```

### Payload Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | The user's question or message to the AI |

### Example Request

```json
{
  "message": "Can you summarize the main points of this lesson?"
}
```

### Backend Processing

The Django backend enriches the payload before sending to the webhook:

```json
{
  "message": "Can you summarize the main points of this lesson?",
  "lesson_id": 11,
  "lesson_title": "Introduction to Time Management",
  "course_name": "Time Management Mastery",
  "user_id": 5,
  "user_email": "student@example.com",
  "chatbot_webhook_id": "d39397da-cf2c-4282-b531-51a321af8586"
}
```

### Webhook Endpoint
**POST** `https://katalyst-crm2.fly.dev/webhook/swi-chatbot`

### Enriched Payload Fields (Sent to Webhook)

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | The user's original question |
| `lesson_id` | integer | Unique identifier for the lesson |
| `lesson_title` | string | The title of the lesson |
| `course_name` | string | The name of the course |
| `user_id` | integer | Unique identifier for the user asking the question |
| `user_email` | string | Email address of the user |
| `chatbot_webhook_id` | string | The webhook ID stored from training (if available) |

### Expected Response

#### Success Response (200 OK)

```json
{
  "success": true,
  "response": "Based on the lesson content, the key strategies include..."
}
```

**OR**

```json
{
  "response": "Based on the lesson content, the key strategies include..."
}
```

**OR**

```json
{
  "message": "Based on the lesson content, the key strategies include..."
}
```

**OR**

```json
{
  "text": "Based on the lesson content, the key strategies include..."
}
```

**OR**

```json
{
  "answer": "Based on the lesson content, the key strategies include..."
}
```

**Note:** The webhook may return the AI response in different field names:
- `response` (preferred)
- `message`
- `text`
- `answer`

The system checks all these fields and uses whichever one is present.

#### Error Response (Non-200 Status)

```json
{
  "error": "Error message describing what went wrong",
  "success": false
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `response` / `message` / `text` / `answer` | string | The AI's response to the user's question |
| `error` | string | Error message if the request failed |

---

## 3. API Endpoints Summary

### Training Endpoint (Internal)

**URL:** `/api/lessons/{lesson_id}/train-chatbot/`  
**Method:** POST  
**Authentication:** Staff required  
**Content-Type:** application/json

**Request:**
```json
{
  "transcript": "Lesson transcript text..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chatbot trained successfully",
  "chatbot_webhook_id": "d39397da-cf2c-4282-b531-51a321af8586"
}
```

### Chatbot Interaction Endpoint (Internal)

**URL:** `/api/lessons/{lesson_id}/chatbot/`  
**Method:** POST  
**Authentication:** Login required + course access  
**Content-Type:** application/json

**Request:**
```json
{
  "message": "User's question here"
}
```

**Response:**
```json
{
  "success": true,
  "response": "AI's answer here"
}
```

---

## 4. Error Handling

### Training Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Transcript is required` | Empty transcript sent | Ensure transcript field is not empty |
| `Webhook returned error: 500` | Training webhook failed | Check webhook service status |
| `Failed to connect to training webhook` | Network error | Check internet connection and webhook URL |

### Chatbot Interaction Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Chatbot is not available for this lesson` | Chatbot not trained | Train the chatbot first |
| `You do not have access to this lesson` | User lacks course access | Grant course access to user |
| `Message is required` | Empty message sent | Ensure message field is not empty |
| `Chatbot webhook returned error: 500` | Chatbot webhook failed | Check webhook service status |

---

## 5. Example cURL Commands

### Train Chatbot

```bash
curl -X POST https://katalyst-crm2.fly.dev/webhook/425e8e67-2aa6-4c50-b67f-0162e2496b51 \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Lesson transcript text here...",
    "lesson_id": 11,
    "lesson_title": "Introduction to Time Management",
    "course_name": "Time Management Mastery",
    "lesson_slug": "introduction-to-time-management"
  }'
```

### Chat with Chatbot

```bash
curl -X POST https://katalyst-crm2.fly.dev/webhook/swi-chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key points in this lesson?",
    "lesson_id": 11,
    "lesson_title": "Introduction to Time Management",
    "course_name": "Time Management Mastery",
    "user_id": 5,
    "user_email": "student@example.com",
    "chatbot_webhook_id": "d39397da-cf2c-4282-b531-51a321af8586"
  }'
```

---

## 6. Webhook URLs

### Training Webhook
```
https://katalyst-crm2.fly.dev/webhook/425e8e67-2aa6-4c50-b67f-0162e2496b51
```

### Chatbot Webhook (Default)
```
https://katalyst-crm2.fly.dev/webhook/swi-chatbot
```

**Note:** The chatbot webhook ID may be returned from the training webhook and stored per lesson. If a lesson-specific webhook ID is stored, it will be used instead of the default.

---

## 7. Data Flow

### Training Flow
1. Admin uploads/pastes transcript → Frontend
2. Frontend sends transcript to `/api/lessons/{id}/train-chatbot/` → Django Backend
3. Django Backend sends enriched payload to Training Webhook → External Service
4. External Service trains AI and returns webhook ID → Django Backend
5. Django Backend stores webhook ID and updates lesson status → Database
6. Frontend receives success response and reloads page

### Chat Flow
1. User types question → Frontend
2. Frontend sends message to `/api/lessons/{id}/chatbot/` → Django Backend
3. Django Backend validates access and enriches payload → Django Backend
4. Django Backend sends enriched payload to Chatbot Webhook → External Service
5. External Service processes question and returns AI response → Django Backend
6. Django Backend returns response to frontend → Frontend
7. Frontend displays AI response to user

---

## 8. Notes

- All timestamps are in UTC
- All text fields should be UTF-8 encoded
- Maximum transcript length: No hard limit, but very large transcripts may timeout
- Maximum message length: Recommended 2000 characters
- Rate limiting: Check with webhook provider for rate limits
- Timeout: 30 seconds for both webhook calls
- Retry logic: Not implemented - failed requests return error immediately

---

## 9. Testing

### Test Training Payload
```json
{
  "transcript": "This is a test transcript for training the AI chatbot. It contains sample lesson content that the AI will learn from.",
  "lesson_id": 999,
  "lesson_title": "Test Lesson",
  "course_name": "Test Course",
  "lesson_slug": "test-lesson"
}
```

### Test Chat Payload
```json
{
  "message": "What is this lesson about?",
  "lesson_id": 999,
  "lesson_title": "Test Lesson",
  "course_name": "Test Course",
  "user_id": 1,
  "user_email": "test@example.com",
  "chatbot_webhook_id": "d39397da-cf2c-4282-b531-51a321af8586"
}
```

---

## 10. Support

For issues or questions about the webhook payloads:
1. Check the error messages in the Django admin logs
2. Verify webhook URLs are correct
3. Ensure all required fields are present
4. Check network connectivity to webhook endpoints
5. Verify authentication/access permissions

