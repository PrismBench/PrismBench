# PrismBench GUI

A web-based interface for submitting and monitoring PrismBench MCTS search experiments.

## Features

- Submit new search jobs with custom session IDs
- Real-time job progress monitoring with polling
- View completed job results and statistics
- Clean, responsive UI built with Next.js and shadcn/ui

## Development

### Prerequisites

- Node.js 18+
- npm

### Local Development

```bash
cd src/services/gui
npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: URL of the Search Service API (default: `http://localhost:8002/api/v1`)

### Docker

```bash
# Build and run with Docker
docker build -t prismgui .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8002/api/v1 prismgui

# Or use docker-compose
docker-compose up gui
```

## Usage

1. **Start a New Job**: Enter a session ID and click "Start Job"
2. **Monitor Progress**: Watch real-time updates of job status and phase progress
3. **View Results**: Completed jobs appear in the results table with duration and status

## API Integration

The GUI communicates with the Search Service API at `/api/v1` with the following endpoints:

- `POST /initialize` - Initialize a new session
- `POST /run` - Start an MCTS task
- `GET /tasks/{task_id}` - Get task status

## Architecture

- **Frontend**: Next.js 14 with TypeScript
- **UI Components**: shadcn/ui (Tailwind CSS + Radix UI)
- **State Management**: React hooks
- **API Client**: Axios
- **Real-time Updates**: Polling every 2 seconds 