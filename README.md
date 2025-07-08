### POST /api/proofread

Description:
Proofreads a given text and returns suggestions for corrections.

Request:
    Headers:
    - Authorization: Bearer <firebase_id_token> (required)
    - Content-Type: application/json
    Body:
    {
    "text": "string" // The text to be proofread.
    }

Response:
 - 200 OK
    {
    "original_text": "string",
    "suggestions": [
        {
        "original": "string",
        "suggested": "string",
        "start": 0,
        "end": 0
        }
        // ...more suggestions
    ]
    }

 - 401 Unauthorized
    { "error": "Missing or invalid Authorization header" }

 - 500 Internal Server Error
    { "error": "Failed to get suggestions from LLM." }

Example cURL:
curl -X POST http://localhost:55000/api/proofread \
  -H "Authorization: Bearer <firebase_id_token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "He go to school everyday. He enjoy to play cricket."}'



### POST /api/modify

Description:
Modifies a specific span of text based on user instructions.

Request: 
Headers: Authorization: Bearer <firebase_id_token> (required) 
Content-Type: application/json 
Body: { "original": "string", // The full original text. "suggested": "string", // The current suggestion for the marked text. "start": 0, // The starting character index (0-based, inclusive). "end": 0, // The ending character index (exclusive). "user_prompt": "string" // The user's instruction for how to modify the text. }

Response: 200 OK { "original": "string", "suggested": "string", // The new suggestion from the LLM. "user_prompt": "string", "start": 0, "end": 0, "ollama_response": "string" // The raw LLM response (may be the same as 'suggested'). }

401 Unauthorized { "error": "Missing or invalid Authorization header" }

500 Internal Server Error { "error": "Failed to get modification from LLM." }

Example cURL: curl -X POST http://localhost:55000/api/modify
-H "Authorization: Bearer <firebase_id_token>"
-H "Content-Type: application/json"
-d '{"original": "He go to school everyday. He enjoy to play cricket.", "suggested": "He enjoys playing", "start": 27, "end": 45, "user_prompt": "Make it sound more formal"}'