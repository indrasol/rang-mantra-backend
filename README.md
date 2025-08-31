# RangMantra Backend

RangMantra is a service that colorizes black and white photos using Google's Gemini AI model. This is the backend API service.

## Features

- Upload black and white images for colorization
- Check status of colorization requests
- Secure storage of both original and colorized images
- Integration with Google's Gemini AI for high-quality colorization
- Supabase storage for user images

## Setup

### Prerequisites

- Python 3.9 or higher
- Supabase account with storage enabled
- Google API key with access to Gemini models

### Installation

1. Clone the repository
2. Navigate to the backend directory:

```bash
cd rang-mantra-backend
```

3. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

6. Update the `.env` file with your:
   - Supabase URL and API keys
   - Google API key

### Database Setup

RangMantra uses Supabase for both authentication and storage. You need to create the following:

1. Storage buckets:
   - `original-images`: For storing uploaded black and white images
   - `colorized-images`: For storing colorized images

2. Database table:
   - `colorize_requests`: For tracking colorization requests

```sql
CREATE TABLE colorize_requests (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  user_email TEXT,
  status TEXT NOT NULL,
  original_path TEXT,
  original_url TEXT,
  colorized_path TEXT,
  colorized_url TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ
);
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at http://localhost:8000/docs

## API Endpoints

- `POST /v1/colorize/upload` - Upload a black and white image for colorization
- `GET /v1/colorize/status/{request_id}` - Check the status of a colorization request

## Environment Variables

See `.env.example` for all required environment variables.