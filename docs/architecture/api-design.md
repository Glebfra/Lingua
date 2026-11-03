# Japanese Language Learning Platform - API Design

## 1. API Overview

### 1.1 Base URL

```
https://api.lingua.example.com/api/v1/
```

### 1.2 Authentication

All authenticated endpoints require JWT token in Authorization header:

```
Authorization: Bearer <jwt_token>
```

### 1.3 Response Format

#### Success Responses

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

#### Error Responses

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "username",
      "message": "Must be between 3 and 150 characters"
    }
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 1.4 Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 100, max: 1000)
- `ordering` - Sort field (`?ordering=-created_at`)

**Response:**
```json
{
  "count": 150,
  "next": "https://api.example.com/api/words/?page=2&page_size=100",
  "previous": null,
  "results": [...]
}
```

### 1.5 Filtering

Standard DRF filtering with additional custom filters:

```
?kanji=猫&page_size=50
&tags=["food", "animals"]
&created_at__gte=2026-01-01
&owner=glebfra
```

### 1.6 Search

Full-text search on Japanese and English fields:

```
?q=猫 food
```

## 2. Authentication Endpoints

### 2.1 Token Obtain

**POST** `/api/token/`

```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc... truncated",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc... truncated"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

**Response Codes:**
- `200` - Success
- `400` - Invalid credentials
- `401` - Authentication failed

### 2.2 Token Refresh

**POST** `/api/token/refresh/`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc... truncated"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc... truncated"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 2.3 Token Destroy

**POST** `/api/token/destroy/`

Headers: `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "success": true,
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 3. User Endpoints

### 3.1 User Profile

**GET** `/api/users/me/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "glebfra",
    "email": "user@example.com",
    "first_name": "Alexey",
    "last_name": "Glebov",
    "native_language": "ru",
    "target_language": "ja",
    "proficiency_level": "beginner",
    "romaji_enabled": true,
    "furigana_enabled": true,
    "show_kanji_stroke_orders": false,
    "total_words_learned": 150,
    "total_sentences_learned": 50,
    "total_study_time_minutes": 180,
    "created_at": "2026-10-01T00:00:00Z",
    "updated_at": "2026-11-02T10:30:00Z",
    "last_active_at": "2026-11-02T09:00:00Z"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

**PATCH** `/api/users/me/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "glebfra",
    "email": "user@example.com",
    "first_name": "Alexey",
    "last_name": "Glebov",
    "native_language": "ru",
    "target_language": "ja",
    "proficiency_level": "beginner",
    "romaji_enabled": true,
    "furigana_enabled": true,
    "show_kanji_stroke_orders": true,
    "total_words_learned": 150,
    "total_sentences_learned": 50,
    "total_study_time_minutes": 180,
    "created_at": "2026-10-01T00:00:00Z",
    "updated_at": "2026-11-02T10:35:00Z",
    "last_active_at": "2026-11-02T10:35:00Z"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:35:00Z"
  }
}
```

### 3.2 User Progress

**GET** `/api/users/me/progress/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_words_mastered": 50,
    "total_sentences_mastered": 20,
    "total_review_count": 500,
    "total_study_time_minutes": 180,
    "average_quiz_score": 85.50,
    "last_reviewed_at": "2026-11-02T09:00:00Z",
    "last_decks_reviewed_at": "2026-11-02T08:30:00Z"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 4. Word Endpoints

### 4.1 Word List

**GET** `/api/words/`

Headers: `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `kanji` - Filter by kanji (e.g., `?kanji=猫`)
- `kana` - Filter by kana (e.g., `?kana=ねこ`)
- `romaji` - Filter by romaji (e.g., `?romaji=neko`)
- `tags` - Filter by tags (e.g., `?tags=food,animals`)
- `word_type` - Filter by type (e.g., `?word_type=noun`)
- `created_by` - Filter by creator username
- `search` - Full-text search (e.g., `?search=猫 food`)

**Response:**
```json
{
  "count": 150,
  "next": "https://api.example.com/api/words/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "kana": "ねこ",
      "kanji": "猫",
      "romaji": "neko",
      "meaning_en": "cat",
      "meanings_en": [
        {
          "text": "a domesticated feline animal",
          "context": "general"
        }
      ],
      "pronunciation": "/neːko̞/",
      "furigana": null,
      "word_type": "noun",
      "tags": ["food", "animals"],
      "created_at": "2026-10-01T00:00:00Z",
      "updated_at": "2026-10-01T00:00:00Z",
      "user": null
    }
  ]
}
```

### 4.2 Word Detail

**GET** `/api/words/{id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "kana": "ねこ",
    "kanji": "猫",
    "romaji": "neko",
    "meaning_en": "cat",
    "meanings_en": [
      {
        "text": "a domesticated feline animal",
        "context": "general"
      }
    ],
    "pronunciation": "/neːko̞/",
    "furigana": null,
    "word_type": "noun",
    "tags": ["food", "animals"],
    "created_at": "2026-10-01T00:00:00Z",
    "updated_at": "2026-10-01T00:00:00Z",
    "user": null
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 4.3 User-Created Words

**GET** `/api/words/user-created/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "count": 10,
  "next": "https://api.example.com/api/words/user-created/?page=2",
  "previous": null,
  "results": [
    {
      "id": 101,
      "kana": "わたし",
      "kanji": "私",
      "romaji": "watashi",
      "meaning_en": "I, me",
      "meanings_en": [],
      "pronunciation": null,
      "furigana": null,
      "word_type": "pronoun",
      "tags": ["personal", "pronouns"],
      "created_at": "2026-11-01T10:00:00Z",
      "updated_at": "2026-11-01T10:00:00Z",
      "user": {
        "id": 1,
        "username": "glebfra",
        "email": "user@example.com",
        "first_name": "Alexey",
        "last_name": "Glebov"
      }
    }
  ]
}
```

**POST** `/api/words/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "kana": "わたし",
  "kanji": "私",
  "romaji": "watashi",
  "meaning_en": "I, me",
  "word_type": "pronoun",
  "tags": ["personal", "pronouns"],
  "pronunciation": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 101,
    "kana": "わたし",
    "kanji": "私",
    "romaji": "watashi",
    "meaning_en": "I, me",
    "meanings_en": [],
    "pronunciation": null,
    "furigana": null,
    "word_type": "pronoun",
    "tags": ["personal", "pronouns"],
    "created_at": "2026-11-02T10:30:00Z",
    "updated_at": "2026-11-02T10:30:00Z",
    "user": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    }
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 4.4 Word Progress

**GET** `/api/words/{word_id}/progress/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "mastery_level": 3,
    "review_count": 15,
    "last_reviewed_at": "2026-11-01T15:00:00Z",
    "next_review_at": "2026-11-03T09:00:00Z",
    "total_attempts": 20,
    "correct_answers": 18,
    "average_score": 90.00,
    "is_mastered": false
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 5. Sentence Endpoints

### 5.1 Sentence List

**GET** `/api/sentences/`

Headers: `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `sentence_type` - Filter by type (e.g., `?sentence_type=question`)
- `tags` - Filter by tags
- `created_by` - Filter by creator username
- `search` - Full-text search (e.g., `?search=猫 food`)

**Response:**
```json
{
  "count": 50,
  "next": "https://api.example.com/api/sentences/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "text": "こんにちは、猫です。",
      "translation": "Hello, I am a cat.",
      "sentence_type": "statement",
      "context": "Greeting or self-introduction",
      "examples": [
        {
          "text": "こんにちは、先生です。",
          "translation": "Hello, I am a teacher."
        }
      ],
      "furigana": "こんにちは (こんにちは)、猫 (ねこ) です (です)。",
      "tags": ["greetings", "basic"],
      "created_at": "2026-10-01T00:00:00Z",
      "updated_at": "2026-10-01T00:00:00Z",
      "user": null
    }
  ]
}
```

### 5.2 Sentence Detail

**GET** `/api/sentences/{id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "text": "こんにちは、猫です。",
    "translation": "Hello, I am a cat.",
    "sentence_type": "statement",
    "context": "Greeting or self-introduction",
    "examples": [
      {
        "text": "こんにちは、先生です。",
        "translation": "Hello, I am a teacher."
      }
    ],
    "furigana": "こんにちは (こんにちは)、猫 (ねこ) です (です)。",
    "tags": ["greetings", "basic"],
    "created_at": "2026-10-01T00:00:00Z",
    "updated_at": "2026-10-01T00:00:00Z",
    "user": null
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 5.3 User-Created Sentences

**GET** `/api/sentences/user-created/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "count": 5,
  "next": "https://api.example.com/api/sentences/user-created/?page=2",
  "previous": null,
  "results": [
    {
      "id": 101,
      "text": "今日は何を食べますか？",
      "translation": "What are you eating today?",
      "sentence_type": "question",
      "context": "Asking about someone's meal",
      "examples": [],
      "furigana": "今日 (きょう) は (は) なに (なに) を (を) たべ (たべ) ます (ます) か (か)？",
      "tags": ["questions", "daily"],
      "created_at": "2026-11-01T10:00:00Z",
      "updated_at": "2026-11-01T10:00:00Z",
      "user": {
        "id": 1,
        "username": "glebfra",
        "email": "user@example.com",
        "first_name": "Alexey",
        "last_name": "Glebov"
      }
    }
  ]
}
```

**POST** `/api/sentences/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "text": "今日は何を食べますか？",
  "sentence_type": "question",
  "context": "Asking about someone's meal",
  "examples": [],
  "furigana": "今日 (きょう) は (は) なに (なに) を (を) たべ (たべ) ます (ます) か (か)？",
  "tags": ["questions", "daily"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 101,
    "text": "今日は何を食べますか？",
    "translation": null,
    "sentence_type": "question",
    "context": "Asking about someone's meal",
    "examples": [],
    "furigana": "今日 (きょう) は (は) なに (なに) を (を) たべ (たべ) ます (ます) か (か)？",
    "tags": ["questions", "daily"],
    "created_at": "2026-11-02T10:30:00Z",
    "updated_at": "2026-11-02T10:30:00Z",
    "user": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    }
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 6. Deck Endpoints

### 6.1 Deck List

**GET** `/api/decks/`

Headers: `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `owner` - Filter by owner username
- `is_shared` - Filter by shared status
- `study_mode` - Filter by study mode
- `search` - Search in deck name and description

**Response:**
```json
{
  "count": 5,
  "next": "https://api.example.com/api/decks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Basic Japanese Words",
      "description": "Essential words for beginners",
      "type": "deck",
      "is_shared": true,
      "owner": {
        "id": 1,
        "username": "glebfra",
        "email": "user@example.com",
        "first_name": "Alexey",
        "last_name": "Glebov"
      },
      "study_mode": "flashcard",
      "show_answer_immediately": false,
      "randomize": true,
      "show_romaji": true,
      "show_kanji": true,
      "show_furigana": false,
      "show_translations": true,
      "item_count": 50,
      "created_at": "2026-10-01T00:00:00Z",
      "updated_at": "2026-10-01T00:00:00Z",
      "shared_with": ["user2", "user3"]
    }
  ]
}
```

### 6.2 Deck Detail

**GET** `/api/decks/{id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Basic Japanese Words",
    "description": "Essential words for beginners",
    "type": "deck",
    "is_shared": true,
    "owner": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    },
    "study_mode": "flashcard",
    "show_answer_immediately": false,
    "randomize": true,
    "show_romaji": true,
    "show_kanji": true,
    "show_furigana": false,
    "show_translations": true,
    "item_count": 50,
    "created_at": "2026-10-01T00:00:00Z",
    "updated_at": "2026-10-01T00:00:00Z",
    "shared_with": ["user2", "user3"],
    "words": [
      {
        "id": 1,
        "kana": "ねこ",
        "kanji": "猫",
        "romaji": "neko",
        "meaning_en": "cat",
        "position": 1,
        "mastery_level": 4,
        "last_reviewed_at": "2026-11-01T15:00:00Z"
      }
    ],
    "sentences": [
      {
        "id": 1,
        "text": "こんにちは、猫です。",
        "translation": "Hello, I am a cat.",
        "position": 5,
        "mastery_level": 2
      }
    ]
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 6.3 Create Deck

**POST** `/api/decks/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "name": "Basic Japanese Words",
  "description": "Essential words for beginners",
  "study_mode": "flashcard",
  "show_answer_immediately": false,
  "randomize": true,
  "show_romaji": true,
  "show_kanji": true,
  "show_furigana": false,
  "show_translations": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Basic Japanese Words",
    "description": "Essential words for beginners",
    "type": "deck",
    "is_shared": false,
    "owner": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    },
    "study_mode": "flashcard",
    "show_answer_immediately": false,
    "randomize": true,
    "show_romaji": true,
    "show_kanji": true,
    "show_furigana": false,
    "show_translations": true,
    "item_count": 0,
    "created_at": "2026-11-02T10:30:00Z",
    "updated_at": "2026-11-02T10:30:00Z",
    "shared_with": []
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 6.4 Add Words/Sentences to Deck

**POST** `/api/decks/{deck_id}/add-items/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "word_ids": [1, 2, 3],
  "sentence_ids": [4, 5]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deck_id": 1,
    "words_added": [
      {
        "id": 1,
        "kana": "ねこ",
        "kanji": "猫",
        "position": 1
      },
      {
        "id": 2,
        "kana": "いぬ",
        "kanji": "犬",
        "position": 2
      }
    ],
    "sentences_added": [
      {
        "id": 4,
        "text": "猫が好きです。",
        "position": 5
      },
      {
        "id": 5,
        "text": "犬が好きです。",
        "position": 6
      }
    ]
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 6.5 Update Deck Item Position

**PUT** `/api/decks/{deck_id}/items/{item_id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "position": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "deck_id": 1,
    "word_id": 1,
    "position": 10,
    "word": {
      "id": 1,
      "kana": "ねこ",
      "kanji": "猫",
      "romaji": "neko",
      "meaning_en": "cat"
    }
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 6.6 Remove Deck Items

**DELETE** `/api/decks/{deck_id}/remove-items/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "word_ids": [1, 2],
  "sentence_ids": [3, 4]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deck_id": 1,
    "words_removed": [1, 2],
    "sentences_removed": [3, 4]
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 6.7 Share Deck

**POST** `/api/decks/{deck_id}/share/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "is_shared": true,
  "shared_with": ["user2", "user3"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Basic Japanese Words",
    "is_shared": true,
    "shared_with": ["user2", "user3"],
    "owner": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    }
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 6.8 Deck Progress

**GET** `/api/decks/{deck_id}/progress/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "deck": {
      "id": 1,
      "name": "Basic Japanese Words"
    },
    "items_reviewed": 50,
    "items_mastered": 30,
    "completion_percentage": 60,
    "total_attempts": 100,
    "correct_answers": 85,
    "average_score": 85.00,
    "started_at": "2026-10-20T00:00:00Z",
    "completed_at": null,
    "last_reviewed_at": "2026-11-01T15:00:00Z",
    "is_completed": false,
    "accuracy": 85.00
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 7. List Endpoints

### 7.1 List List

**GET** `/api/lists/`

Headers: `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `owner` - Filter by owner username
- `search` - Search in list name and description

**Response:**
```json
{
  "count": 3,
  "next": "https://api.example.com/api/lists/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Favorite Food Words",
      "description": "Words related to food I like",
      "type": "list",
      "is_shared": false,
      "owner": {
        "id": 1,
        "username": "glebfra",
        "email": "user@example.com",
        "first_name": "Alexey",
        "last_name": "Glebov"
      },
      "item_count": 25,
      "created_at": "2026-10-15T00:00:00Z",
      "updated_at": "2026-10-15T00:00:00Z",
      "shared_with": [],
      "words": [
        {
          "id": 1,
          "kana": "すし",
          "kanji": "寿司",
          "romaji": "sushi",
          "meaning_en": "sushi",
          "position": 1
        },
        {
          "id": 2,
          "kana": "らーめん",
          "kanji": "ラーメン",
          "romaji": "ramen",
          "meaning_en": "ramen",
          "position": 2
        }
      ]
    }
  ]
}
```

### 7.2 Create List

**POST** `/api/lists/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "name": "Favorite Food Words",
  "description": "Words related to food I like"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Favorite Food Words",
    "description": "Words related to food I like",
    "type": "list",
    "is_shared": false,
    "owner": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    },
    "item_count": 0,
    "created_at": "2026-11-02T10:30:00Z",
    "updated_at": "2026-11-02T10:30:00Z",
    "shared_with": [],
    "words": []
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 7.3 Add Items to List

**POST** `/api/lists/{list_id}/add-items/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "word_ids": [1, 2, 3],
  "sentence_ids": []
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "list_id": 1,
    "words_added": [
      {
        "id": 1,
        "kana": "すし",
        "kanji": "寿司",
        "position": 1
      }
    ]
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 8. Import Endpoints

### 8.1 Import Job List

**GET** `/api/imports/jobs/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "count": 3,
  "next": "https://api.example.com/api/imports/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "glebfra",
        "email": "user@example.com",
        "first_name": "Alexey",
        "last_name": "Glebov"
      },
      "import_type": "csv",
      "file_name": "words_japanese.csv",
      "file_size": 10240,
      "total_items": 100,
      "successful_items": 98,
      "failed_items": 2,
      "status": "completed",
      "error_message": "",
      "created_at": "2026-10-25T10:00:00Z",
      "completed_at": "2026-10-25T10:01:00Z",
      "success_rate": 98.00
    }
  ]
}
```

### 8.2 Upload File

**POST** `/api/imports/upload/`

Headers: `Authorization: Bearer <jwt_token>`

**Content-Type:** `multipart/form-data`

**Request:**
- `import_type` (file): CSV or JSON file
- `file` (file): The import file

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": 1,
    "status": "processing",
    "file_name": "words_japanese.csv",
    "file_size": 10240,
    "estimated_completion": "2026-10-25T10:01:00Z"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 8.3 Import Job Detail

**GET** `/api/imports/jobs/{job_id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    },
    "import_type": "csv",
    "file_name": "words_japanese.csv",
    "file_size": 10240,
    "total_items": 100,
    "successful_items": 98,
    "failed_items": 2,
    "status": "completed",
    "error_message": "",
    "created_at": "2026-10-25T10:00:00Z",
    "completed_at": "2026-10-25T10:01:00Z",
    "success_rate": 98.00,
    "import_items": [
      {
        "row_number": 1,
        "item_type": "word",
        "status": "success",
        "created_entities": [1, 2, 3]
      },
      {
        "row_number": 50,
        "item_type": "word",
        "status": "duplicate",
        "updated_entities": [45]
      }
    ]
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 8.4 Cancel Import Job

**POST** `/api/imports/jobs/{job_id}/cancel/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": 1,
    "status": "cancelled"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 9. Note Endpoints

### 9.1 Notes List

**GET** `/api/notes/`

Headers: `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `target_type` - Filter by target type (word, sentence, deck)
- `target_id` - Filter by target ID
- `is_public` - Filter by public status
- `created_by` - Filter by creator username

**Response:**
```json
{
  "count": 5,
  "next": "https://api.example.com/api/notes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "note_type": "word_note",
      "target_type": "word",
      "target_id": 1,
      "title": "猫 - Additional Notes",
      "content": "This word can also mean 'person' in some contexts.",
      "is_public": false,
      "user": {
        "id": 1,
        "username": "glebfra",
        "email": "user@example.com",
        "first_name": "Alexey",
        "last_name": "Glebov"
      },
      "created_at": "2026-10-20T10:00:00Z",
      "updated_at": "2026-10-20T10:00:00Z"
    }
  ]
}
```

### 9.2 Create Note

**POST** `/api/notes/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "note_type": "word_note",
  "target_type": "word",
  "target_id": 1,
  "title": "猫 - Additional Notes",
  "content": "This word can also mean 'person' in some contexts.",
  "is_public": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "note_type": "word_note",
    "target_type": "word",
    "target_id": 1,
    "title": "猫 - Additional Notes",
    "content": "This word can also mean 'person' in some contexts.",
    "is_public": false,
    "user": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    },
    "created_at": "2026-11-02T10:30:00Z",
    "updated_at": "2026-11-02T10:30:00Z"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 9.3 Update Note

**PATCH** `/api/notes/{id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Request:**
```json
{
  "title": "猫 - Updated Notes",
  "content": "Updated content with new information.",
  "is_public": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "note_type": "word_note",
    "target_type": "word",
    "target_id": 1,
    "title": "猫 - Updated Notes",
    "content": "Updated content with new information.",
    "is_public": true,
    "user": {
      "id": 1,
      "username": "glebfra",
      "email": "user@example.com",
      "first_name": "Alexey",
      "last_name": "Glebov"
    },
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-11-02T10:30:00Z"
  },
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

### 9.4 Delete Note

**DELETE** `/api/notes/{id}/`

Headers: `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "meta": {
    "request_id": "abc123",
    "timestamp": "2026-11-02T10:30:00Z"
  }
}
```

## 10. Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_TOKEN_MISSING` | 401 | Authorization header missing |
| `AUTH_TOKEN_INVALID` | 401 | Invalid or expired token |
| `AUTH_TOKEN_EXPIRED` | 401 | Token has expired |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `UNAUTHORIZED` | 403 | User not authorized for this action |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `BAD_REQUEST` | 400 | Invalid request format |
| `INTERNAL_ERROR` | 500 | Internal server error |

## 11. Rate Limiting

All authenticated endpoints are rate-limited:

- **Standard limit**: 100 requests per minute per user
- **Burst limit**: 20 requests per second
- **Exceeding limits**: 429 Too Many Requests with `Retry-After` header

## 12. Versioning

Current API version: `v1`

All URLs include version prefix: `/api/v1/`

Future versioning will use URL prefix (e.g., `/api/v2/`).

## 13. OpenAPI Specification

Full OpenAPI 3.0 specification is auto-generated from Django REST Framework serializers and viewsets.

Location: `https://api.lingua.example.com/api/openapi.yaml`
