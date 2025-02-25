# SearchAI

An AI Search Engine that provides intelligent search functionality with real-time processing and result management.

~2k LOC

![alt text](image.png)

## Features

- Real-time search processing with progress tracking
- Asynchronous search operations
- Source content detail viewing
- Search result management (including deletion)
- Interactive user interface

## Technical Stack

- Frontend: React.js
- Backend: fastAPI server running on port 8000
- Communication: Axios for HTTP requests

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SearchAI.git
cd SearchAI
```

2. Install dependencies:
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

## Usage

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Access the application at `http://localhost:3000`

## API Endpoints

- `GET /data/` - Fetch all scraped data
- `GET /search/` - Perform a search query
- `GET /source_detail` - Get detailed content for a specific source
- `POST /cancel/{searchId}` - Cancel an ongoing search
- `DELETE /search/{query}` - Delete search results

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
