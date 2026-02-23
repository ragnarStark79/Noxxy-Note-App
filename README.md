# 📝 Noxxy - Note Taking Application

A clean, scalable Flask + MongoDB note-taking REST API built with best practices and clean architecture.

## 🚀 Features

- ✅ Create, read, update notes
- 🗑️ Soft delete notes (move to bin)
- ♻️ Restore notes from bin
- 🗄️ Permanently delete notes
- 📌 Pin/unpin notes
- 📁 Organize notes with folders
- 🔍 List notes (pinned first)
- 🎯 Filter notes by folder

## 🛠️ Tech Stack

- **Flask** - Web framework
- **PyMongo** - MongoDB driver
- **MongoDB** - Database
- **Flask-CORS** - CORS support
- **python-dotenv** - Environment configuration
- **uv** - Package management

## 📁 Project Structure

```
Noxxy/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # MongoDB initialization
│   ├── models/              # Database layer
│   │   ├── note_model.py
│   │   └── folder_model.py
│   ├── services/            # Business logic
│   │   ├── note_service.py
│   │   └── folder_service.py
│   ├── routes/              # API endpoints
│   │   ├── note_routes.py
│   │   ├── bin_routes.py
│   │   └── folder_routes.py
│   └── utils/               # Helper functions
│       └── helpers.py
├── run.py                   # Application entry point
└── .env                     # Environment variables
```

## 🏃 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB (running locally or remote)
- uv package manager

### Installation

1. **Clone the repository**
```bash
cd Noxxy
```

2. **Install dependencies**
```bash
uv sync
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB URI
```

4. **Start MongoDB** (if running locally)
```bash
# macOS with Homebrew
brew services start mongodb-community

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

5. **Run the application**
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## 📝 Notes Endpoints

### Create Note
```http
POST /notes
Content-Type: application/json

{
  "title": "My Note",
  "content": "Note content here",
  "folder_id": "optional-folder-id"
}
```

**Response:** `201 Created`

---

### Get Note
```http
GET /notes/:note_id
```

**Response:** `200 OK`

---

### Update Note
```http
PUT /notes/:note_id
Content-Type: application/json

{
  "title": "Updated title",
  "content": "Updated content"
}
```

**Response:** `200 OK`

---

### Delete Note (Soft Delete)
```http
DELETE /notes/:note_id
```

**Response:** `200 OK` - Moves note to bin

---

### Toggle Pin
```http
PATCH /notes/:note_id/pin
```

**Response:** `200 OK`

---

### List Notes
```http
GET /notes
GET /notes?folder_id=:folder_id
```

**Response:** `200 OK` - Returns pinned notes first, then by creation date

---

## 🗑️ Bin Endpoints

### List Deleted Notes
```http
GET /bin
```

**Response:** `200 OK`

---

### Restore Note
```http
PATCH /bin/:note_id/restore
```

**Response:** `200 OK`

---

### Permanently Delete Note
```http
DELETE /bin/:note_id
```

**Response:** `200 OK` - Cannot be undone

---

## 📁 Folders Endpoints

### Create Folder
```http
POST /folders
Content-Type: application/json

{
  "name": "Work"
}
```

**Response:** `201 Created`

---

### List Folders
```http
GET /folders
```

**Response:** `200 OK` - Includes note count for each folder

---

### Get Folder
```http
GET /folders/:folder_id
```

**Response:** `200 OK`

---

### Delete Folder
```http
DELETE /folders/:folder_id
DELETE /folders/:folder_id?remove_notes=true
```

**Response:** `200 OK`

---

### Add Note to Folder
```http
PATCH /folders/:folder_id/notes/:note_id
```

**Response:** `200 OK`

---

### Remove Note from Folder
```http
DELETE /folders/:folder_id/notes/:note_id
```

**Response:** `200 OK`

---

## 📊 Data Models

### Note Document
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Note title",
  "content": "Note content",
  "is_pinned": false,
  "is_deleted": false,
  "folder_id": "507f1f77bcf86cd799439012",
  "created_at": "2026-02-09T10:00:00",
  "updated_at": "2026-02-09T10:00:00"
}
```

### Folder Document
```json
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Work",
  "note_count": 5,
  "created_at": "2026-02-09T10:00:00"
}
```

---

## 🧪 Testing

Example using curl:

```bash
# Create a note
curl -X POST http://localhost:5001/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Note", "content": "Hello World"}'

# List notes
curl http://localhost:5001/notes

# Pin a note
curl -X PATCH http://localhost:5001/notes/NOTE_ID/pin

# Create a folder
curl -X POST http://localhost:5001/folders \
  -H "Content-Type: application/json" \
  -d '{"name": "Work"}'

# Add note to folder
curl -X PATCH http://localhost:5001/folders/FOLDER_ID/notes/NOTE_ID

# Delete note (move to bin)
curl -X DELETE http://localhost:5001/notes/NOTE_ID

# List bin
curl http://localhost:5001/bin

# Restore from bin
curl -X PATCH http://localhost:5001/bin/NOTE_ID/restore
```

---

## 🏗️ Architecture

### Separation of Concerns

- **Routes** - HTTP request/response handling only
- **Services** - Business logic and validation
- **Models** - Database operations (PyMongo)
- **Utils** - Helper functions

### Design Patterns

- **App Factory Pattern** - For flexible app creation
- **Blueprint Pattern** - For modular routes
- **Service Layer Pattern** - For business logic separation

---

## ⚙️ Configuration

Environment variables in `.env`:

```env
MONGO_URI=mongodb://localhost:27017/noxxy
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
```

---

## 🔒 Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `405` - Method Not Allowed
- `500` - Internal Server Error

---

## 📝 Notes

- No authentication implemented (add JWT/OAuth if needed)
- IDs are MongoDB ObjectIds (24-character hex strings)
- All timestamps in UTC ISO format
- Soft delete keeps notes in database
- Pinned notes always appear first in listings

---

## 🤝 Contributing

Follow clean code principles:
- Write descriptive comments
- Keep functions small and focused
- Use type hints
- Handle errors gracefully
- Return meaningful error messages

---

## 📄 License

MIT License

---

Built with ❤️ using Flask and MongoDB

