# UPLO5 - AI Virtual Try-On Fashion App

[![GitHub](https://img.shields.io/github/license/RooJenkins/UPLO5)](https://github.com/RooJenkins/UPLO5)
[![React Native](https://img.shields.io/badge/React%20Native-0.74-blue)](https://reactnative.dev/)
[![Expo](https://img.shields.io/badge/Expo-SDK%2051-black)](https://expo.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-Flash%202.5-orange)](https://ai.google.dev/)

> TikTok-style mobile app for AI-powered virtual try-on with real fashion products from major brands.

![UPLO5 Demo](https://via.placeholder.com/800x400?text=UPLO5+Virtual+Try-On+Demo)

## ✨ Features

- 🤖 **AI-Powered Virtual Try-On** - See yourself in real clothing using Gemini Flash 2.5
- 👗 **Real Products** - 2000+ items from ASOS, H&M, Zara, Nike
- 📱 **Infinite Scroll** - TikTok-style feed with smooth 60fps performance
- ⚡ **30-Worker System** - Parallel AI generation for instant results
- 🎯 **Smart Preloading** - Next 5 items loaded before you scroll
- 🛍️ **Shop Now** - Direct links to purchase products

## 🚀 Quick Start

### Mobile App

```bash
# Install dependencies
npm install
# or
bun install

# Start development server
npx expo start

# Run on iOS/Android
npx expo start --ios
npx expo start --android
```

### Catalog Service

```bash
# Navigate to backend
cd catalog-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000

# Scrape products (optional)
python -m scraper.run --all --limit 500
```

## 📋 Requirements

- **Node.js** 18+ or Bun
- **Python** 3.10+
- **PostgreSQL** 15+ (or Supabase account)
- **Expo Go** app (for mobile testing)
- **iOS Simulator** or **Android Emulator** (optional)

## 🏗️ Architecture

```
┌────────────────────────────────────────────┐
│         UPLO5 System Architecture          │
├────────────────────────────────────────────┤
│                                            │
│  Mobile App (React Native + Expo)         │
│    ├── 30-Worker AI Generation            │
│    ├── Infinite Scroll Feed               │
│    └── Smart Image Preloading             │
│                                            │
│  Catalog Service (FastAPI + PostgreSQL)   │
│    ├── Product Database (2000+ items)     │
│    ├── REST API (port 8000)               │
│    └── Web Scrapers (ASOS, H&M, etc.)     │
│                                            │
│  AI Service (Rork API)                     │
│    └── Gemini Flash 2.5 Backend           │
│                                            │
└────────────────────────────────────────────┘
```

## 📖 Documentation

- **[PRD.md](PRD.md)** - Complete product requirements
- **[CLAUDE.md](CLAUDE.md)** - AI assistant development guide
- **[API_DOCS.md](API_DOCS.md)** - API endpoint documentation (coming soon)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide (coming soon)

## 🎯 Project Structure

```
UPLO5/
├── .claude/
│   └── agents/             # AI agent definitions (8 specialized agents)
├── app/                    # React Native app
│   ├── (main)/
│   │   └── feed.tsx       # Main feed screen
│   ├── onboarding.tsx     # Photo upload
│   └── _layout.tsx        # Root layout
├── catalog-service/        # Python backend
│   ├── app/               # FastAPI application
│   ├── scraper/           # Web scrapers
│   ├── alembic/           # DB migrations
│   └── tests/             # Backend tests
├── components/            # Reusable UI components
├── lib/                   # Core services
│   ├── RorkAIClient.ts   # AI integration
│   └── FeedLoadingService.ts  # 30-worker system
├── providers/             # React Context
├── PRD.md                 # Product requirements
├── CLAUDE.md              # AI development guide
└── README.md              # This file
```

## 🧪 Testing

```bash
# Mobile app tests
npm test

# Backend tests
cd catalog-service
pytest

# Test coverage
npm test -- --coverage
pytest --cov=app tests/
```

## 🚢 Deployment

### Mobile App
- **Expo Go**: For development/testing
- **EAS Build**: For production iOS/Android builds
- **Expo Update**: For OTA updates

### Backend
- **Vercel** / **Railway** / **Fly.io**: FastAPI deployment
- **Supabase**: Managed PostgreSQL hosting

## 🤝 Contributing

This project uses an agent-based development workflow. See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

### Development Team (AI Agents)

All agents use **Sonnet 4.5**:

1. **System Architect** - Architecture & database design
2. **Backend API Engineer** - FastAPI development
3. **Web Scraper Engineer** - Product data collection
4. **React Native Developer** - Mobile UI
5. **AI Integration Specialist** - Gemini/Rork API
6. **Performance Engineer** - 30-worker system & optimization
7. **QA Test Engineer** - Testing & quality assurance
8. **Documentation Specialist** - Documentation

## 🔒 Security & Privacy

- User photos stored locally only (not uploaded to servers)
- Product data is publicly available
- All API requests use HTTPS
- No user authentication required
- Open source (MIT License)

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Scroll FPS | 60fps | ✅ |
| Worker Count | 30 active | ✅ |
| Generation Time | <3s avg | ✅ |
| Buffer Health | 80%+ | ✅ |
| Memory Usage | <200MB | ⚠️ |

## 🐛 Known Issues

See [GitHub Issues](https://github.com/RooJenkins/UPLO5/issues) for current bugs and feature requests.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rork** for providing Gemini Flash 2.5 API access
- **Anthropic** for Claude Sonnet 4.5
- **Expo** for amazing React Native tooling
- **FastAPI** for the excellent Python framework

## 📞 Contact

- **GitHub**: [@RooJenkins](https://github.com/RooJenkins)
- **Project**: [UPLO5](https://github.com/RooJenkins/UPLO5)

---

**Built with ❤️ using AI-powered development (Claude Sonnet 4.5)**
