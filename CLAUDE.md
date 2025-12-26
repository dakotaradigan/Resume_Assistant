# CLAUDE.md

This file provides development guidance for the Resume Assistant chatbot project.

## CRITICAL: This is a NEW Project

**IMPORTANT**: This is a completely NEW chatbot project for Dakota's personal resume/portfolio.

**DO NOT:**
- Copy code from other projects (e.g., Ben AI chatbot in Documents folder)
- Reference other codebases except for learning architectural patterns
- Assume implementations from other projects apply here

**DO:**
- Build everything from scratch for THIS use case
- Reference other projects ONLY to understand patterns (e.g., "Ben AI used FastAPI, we can use that framework too")
- Ask before making assumptions based on other codebases

**Ben AI chatbot** exists in `/Users/dakotaradigan/Documents/chatbot_benai_enhanced_UI/` and can be referenced for:
- Understanding FastAPI structure
- Learning WebSocket patterns
- Seeing UI component organization
BUT: Do NOT copy code directly - this is a different use case with different requirements.

---

## Project Overview

**Resume Assistant** is a personal AI-powered chatbot designed to showcase Dakota Radigan's professional experience, skills, and projects to recruiters and hiring managers. This serves dual purposes:
1. **Functional**: Provide an interactive way for visitors to learn about Dakota's background
2. **Technical Showcase**: Demonstrate expertise in RAG (Retrieval Augmented Generation), vector search, multimodal AI, and modern web development

**Deployment Target**: Public website accessible via LinkedIn profile link

**Target Audience**: Recruiters, hiring managers, potential collaborators visiting from LinkedIn

---

## Core Goals & Requirements

### Primary Objectives
1. **Personal Branding**: Create a unique, memorable way to present professional background
2. **Skill Demonstration**: Actively showcase RAG, vector search, and multimodal AI capabilities
3. **Accessibility**: Public deployment that handles concurrent visitors efficiently
4. **Ease of Updates**: Frequent content updates during active job search (weekly/bi-weekly)

### Technical Showcase Priorities
**MUST demonstrate these skills prominently:**
- - **RAG Architecture**: Semantic search over resume/project documents
- - **Vector Database**: Qdrant or Chroma for document retrieval
- - **Multimodal AI**: Claude Sonnet for text + image analysis (project screenshots, diagrams)
- - **Real-time Communication**: WebSocket implementation
- - **Clean UI/UX**: Professional, Claude-inspired interface

### Content Types
- **Text Data**: Resume JSON, project descriptions (markdown), work experience narratives
- **Documents**: PDFs (can be processed and embedded)
- **Images**: Project screenshots, architecture diagrams, UI mockups (for multimodal analysis)
- **Structured Data**: Skills taxonomy, timeline data, contact information

---

## Architecture Decisions

### Tech Stack (Final Decision)

**Backend:**
- **Framework**: FastAPI (proven from Ben AI chatbot)
- **Communication**: WebSocket primary, REST fallback
- **Vector DB**: Qdrant (free tier, better than Pinecone for small-scale, easy Docker deployment)
- **AI Model**: Claude Sonnet 3.5 (multimodal support for images, excellent for conversational AI)
- **Embeddings**: Voyage AI or OpenAI text-embedding-3-small
- **Session Management**: In-memory (same as Ben AI)

**Frontend:**
- **Framework**: Vanilla JavaScript (modular architecture from Ben AI chatbot)
- **UI Style**: Claude-inspired clean design with personal branding
- **Components**: ChatManager, WebSocketManager, SidebarManager (adapted from Ben AI)
- **Enhancements**: Project gallery, skill visualizations, contact links

**Data Layer:**
- **Primary**: `data/resume.json` (structured career data)
- **Projects**: `data/projects/*.md` (detailed project writeups)
- **Media**: `data/images/` (project screenshots, diagrams)
- **Vector Index**: Qdrant collection with chunked documents + metadata

**Deployment:**
- **Hosting**: Railway or Render (backend), Vercel (frontend) OR all-in-one
- **Database**: Qdrant Cloud free tier OR self-hosted in Docker
- **Domain**: Custom subdomain (e.g., chat.dakotaradigan.com or assistant.dakotaradigan.com)

### Why These Choices?

**Why Qdrant over Pinecone?**
- Free tier supports 1GB storage (enough for this use case)
- Better for small-scale deployments
- Docker support for self-hosting option
- Lower latency for small datasets
- No $70/month minimum like Pinecone

**Why Claude over GPT-4?**
- Native multimodal support (text + images in same conversation)
- Better for conversational, nuanced responses
- 200k context window (can handle large resume corpus)
- Showcases diversity in AI model experience

**Why Keep WebSocket Architecture?**
- Demonstrates real-time system design skills
- Better UX (typing indicators, instant responses)
- Proven implementation from Ben AI chatbot
- Differentiates from simple chat interfaces

---

## Phase-Based Development Approach

### **CRITICAL: Incremental Development Philosophy**
This project will be built in discrete phases. **DO NOT attempt to build everything at once.** Each phase should be completable in 1-2 focused work sessions and fully functional before moving to the next.

---

### Phase 1: Project Foundation & Data Structure
**Goal**: Set up project skeleton and define data schemas

**Tasks:**
1. Create folder structure (backend/, frontend/, data/, docs/)
2. Define resume.json schema with Dakota's actual data
3. Create 2-3 sample project markdown files
4. Set up requirements.txt with core dependencies
5. Create .env.example template
6. Write initial system_prompt.txt

**Deliverables:**
- - Clean project structure
- - Populated resume.json with real data
- - Sample project descriptions
- - Dependencies documented

**Exit Criteria**: All data files created and validated, no code yet

---

### Phase 2: Basic FastAPI Backend (No Vector DB Yet)
**Goal**: Get basic chat working with context-only approach first

**Tasks:**
1. Create minimal FastAPI app (health endpoint, basic chat endpoint)
2. Implement session management (copy from Ben AI)
3. Add Claude API integration with resume context in system prompt
4. Test basic conversational responses about resume
5. Add CORS configuration for frontend

**Deliverables:**
- - Working REST API endpoint /api/chat
- - Claude integration with full resume context
- - Basic conversational responses work

**Exit Criteria**: Can ask questions about Dakota's experience and get accurate responses via REST API

---

### Phase 3: Vector Search Implementation (RAG Layer)
**Goal**: Add semantic search capability to showcase RAG skills

**Tasks:**
1. Set up Qdrant (local Docker first, then cloud)
2. Implement document chunking strategy for projects/resume sections
3. Create embedding pipeline (Voyage AI or OpenAI)
4. Build vector search function with metadata filtering
5. Integrate retrieval into chat endpoint (context + retrieved docs)
6. Add function calling for structured queries (optional)

**Deliverables:**
- - Qdrant collection populated with resume documents
- - Semantic search working ("Show me AI projects" returns relevant docs)
- - RAG pipeline integrated into responses

**Exit Criteria**: Questions about specific skills/projects retrieve relevant context from vector DB

---

### Phase 4: Multimodal Support (Image Analysis)
**Goal**: Demonstrate multimodal AI capability with project visuals

**Tasks:**
1. Add image storage strategy (local files or cloud storage)
2. Update data schema to include image references per project
3. Implement image encoding for Claude API
4. Create queries that trigger image analysis ("Show me the Ben AI interface")
5. Update frontend to display images in chat

**Deliverables:**
- - Project screenshots stored and accessible
- - Claude can analyze and describe project images
- - Images display inline in chat responses

**Exit Criteria**: Can ask "What does the X project look like?" and get image + analysis

---

### Phase 5: WebSocket Real-Time Communication
**Goal**: Add WebSocket for better UX and technical showcase

**Tasks:**
1. Implement WebSocket endpoint (copy from Ben AI chatbot)
2. Add ConnectionManager class for session management
3. Create typing indicators
4. Add ping/pong heartbeat mechanism
5. Implement fallback to REST if WebSocket fails

**Deliverables:**
- - WebSocket endpoint /ws/{session_id}
- - Real-time message streaming
- - Typing indicators working

**Exit Criteria**: Chat feels responsive with instant feedback, degrades gracefully to REST

---

### Phase 6: Frontend Development
**Goal**: Build professional, branded chat interface

**Tasks:**
1. Copy Ben AI frontend structure (HTML, CSS, JS modules)
2. Customize branding (colors, logo, personal touches)
3. Update sidebar with resume-specific quick queries
4. Add header with Download Resume PDF, LinkedIn, GitHub links
5. Create project gallery view (optional enhancement)
6. Implement WebSocket client with fallback

**Deliverables:**
- - Responsive chat interface
- - Personal branding applied
- - Quick-start suggestions tailored to resume
- - Contact/social links in header

**Exit Criteria**: Fully functional UI that feels professional and personal

---

### Phase 7: Deployment & Public Access
**Goal**: Deploy to production and make publicly accessible

**Tasks:**
1. Set up Qdrant Cloud free tier (or Docker on Railway/Render)
2. Deploy backend to Railway/Render with environment variables
3. Deploy frontend to Vercel (or static hosting)
4. Configure custom domain/subdomain
5. Add analytics (optional: track visitor interactions)
6. Test from external network (not localhost)
7. Create LinkedIn post announcing the assistant

**Deliverables:**
- - Public URL live and accessible
- - SSL/HTTPS configured
- - Environment variables secured
- - LinkedIn profile updated with link

**Exit Criteria**: Can share URL with recruiters, fully functional from any device

---

### Phase 8: Polish & Enhancements (Post-Launch)
**Goal**: Iterative improvements based on usage

**Possible Enhancements:**
- Skill tag visualization (interactive word cloud)
- Timeline view of career progression
- "Ask about..." suggested queries based on visitor patterns
- PDF resume generation from chat ("Can you email me Dakota's resume?")
- A/B testing different system prompts
- Usage analytics dashboard

**Priority**: Low (only after core functionality proven)

---

## Development Workflow Preferences

### User's Preferences (DO NOT VIOLATE)
1. **Incremental Development**: Build one phase at a time, get it working before moving on
2. **Explain Before Coding**: Justify changes and explain why they're necessary
3. **No One-Shot Builds**: Break large changes into reviewable chunks
4. **Test Each Phase**: Ensure functionality before proceeding to next phase

## Production & Scalability Guardrails
- **State & Sessions**: Anything stateful (sessions/chat history/rate limits) must be pluggable. Default to in-memory for local dev; plan to swap to a shared store (e.g., Redis) when running multiple workers/containers.
- **Config**: All secrets/URLs via environment variables; keep `.env.example` current. No hardcoded keys.
- **Model Selection**: Use `ANTHROPIC_MODEL` env; default `claude-opus-latest`. Pin a dated model only if you need deterministic behavior.
- **Timeouts/Retries**: Set sensible client/server timeouts and return user-friendly errors on upstream failures.
- **Streaming**: Prefer streaming responses for UX; keep REST fallback.
- **CORS/Security**: Tighten allowed origins for production; add security headers (CSP, etc.) before go-live.
- **Logging/Metrics**: Structured logs (omit PII); track latency/error rates. Include health and readiness probes.
- **Testing/CI**: Add smoke tests (`/health`) and mocked chat tests; run lint/format in CI.
- **Static Assets**: Frontend should build as static assets; avoid coupling to backend hostnames (use relative paths or configurable base URLs).
- **RAG Layer**: Keep retrieval behind a small interface so local/Qdrant/cloud backends can swap without touching chat handlers.
- **Rate Limits/Abuse**: Plan for simple per-session/IP rate limits in production.
- **Deploy Targets**: Default assumption—backend on Railway/Render + Qdrant Cloud or containerized Qdrant; frontend on Vercel/static hosting; custom domain with HTTPS.

### Code Quality Standards

**CRITICAL PRINCIPLE: Avoid Technical Debt from Day One**

This project must remain clean, organized, and maintainable throughout development. Dakota wants to avoid technical debt and keep the codebase easy to understand for anyone who reviews it.

**Technical Debt Prevention:**
- Write code as if someone will read it in 6 months with no context
- No "temporary" hacks or "we'll fix this later" solutions
- If something feels messy, refactor it immediately before moving forward
- Delete unused code immediately - don't comment it out "just in case"
- Every function/class should have a single, clear purpose

**Project Organization Principles:**
1. **Minimal File Structure**: Keep it simple - no unnecessary folders or abstractions
2. **Clear Naming**: File and variable names should be self-explanatory
3. **Logical Grouping**: Related code stays together, unrelated code stays separate
4. **No Premature Optimization**: Build for clarity first, optimize only when needed
5. **Documentation Where It Matters**: Comments explain WHY, not WHAT (code should be self-documenting)

**Code Patterns to Follow:**
- Clear variable naming (e.g., `user_message`, `resume_data`, not `msg`, `data`)
- Comments only for complex logic that isn't self-evident
- Modular design: separate concerns (routing, AI logic, data access)
- Error handling with specific, helpful messages
- Logging for debugging and monitoring (but not excessive)
- Type hints in Python where they add clarity

**Code Patterns to AVOID:**
- Deeply nested folders (backend/services/api/v1/handlers/... NO!)
- Overly abstract classes (e.g., BaseAbstractFactoryManager)
- Unused imports or dead code
- Magic numbers or strings (use constants with clear names)
- God functions (one function doing 10 different things)
- Copy-pasted code (create a reusable function instead)

**When Writing Code:**
1. **Think**: Is this the simplest solution that solves the problem?
2. **Write**: Implement cleanly with clear naming
3. **Review**: Would a stranger understand this code?
4. **Refactor**: If it feels messy, clean it up NOW (not later)
5. **Test**: Verify it works before moving to the next task

**Red Flags to Watch For:**
- "I'll clean this up later" ← Do it now
- "This is a temporary hack" ← Find the right solution now
- "I'm not sure what this does anymore" ← Refactor immediately
- "Let me just copy this function and modify it" ← Abstract the common logic
- "This file is getting long, but it's fine" ← Split it into logical modules

**Remember**: This is a portfolio piece. Every file someone looks at should demonstrate clean, professional engineering. Technical debt compounds quickly - prevent it from the start.

---

## Key Differentiators from Ben AI Chatbot

| Aspect | Ben AI Chatbot | Resume Assistant |
|--------|----------------|------------------|
| **Purpose** | Financial advisor tool (B2B) | Personal portfolio (B2C) |
| **Data Volume** | 40+ benchmarks, structured | 5-10 projects, semi-structured |
| **Query Style** | Deterministic lookups ("What's the minimum?") | Conversational exploration ("Tell me about...") |
| **Vector DB** | Pinecone (enterprise) | Qdrant (free tier, smaller scale) |
| **AI Model** | OpenAI GPT-4 | Claude Sonnet (multimodal) |
| **Multimodal** | No | Yes (project images, diagrams) |
| **Function Calling** | 3 complex functions (required) | 1-2 simple functions (optional) |
| **Security** | High (prevent hallucination, financial context) | Moderate (personal data, no sensitive info) |
| **Updates** | Periodic (monthly benchmark data) | Frequent (weekly during job search) |
| **Access** | Internal tool | Public website |

---

## Content Structure

### resume.json Schema (To Be Populated)
```
{
  "personal": {name, title, location, contact, links, summary},
  "experience": [{company, role, duration, achievements, technologies}],
  "projects": [{name, tech_stack, description, highlights, links, images}],
  "skills": {languages, frameworks, ai_ml, databases, tools},
  "education": [{degree, school, graduation, details}],
  "certifications": [{name, issuer, date}] (optional),
  "achievements": [{title, description, date}] (optional)
}
```

### Project Markdown Template
```
# Project Name

## Overview
Brief description of the project and its purpose

## Problem Solved
What challenge did this address?

## Technical Implementation
- Architecture decisions
- Key technologies used
- Interesting engineering challenges

## Impact/Results
Quantifiable outcomes if available

## Images
- screenshots/architecture-diagram.png
- screenshots/ui-mockup.png
```

---

## Common Queries to Optimize For

The assistant should excel at answering:
- "What experience does Dakota have with [technology]?"
- "Tell me about Dakota's AI/ML projects"
- "What companies has Dakota worked for?"
- "Does Dakota know [programming language/framework]?"
- "Show me examples of Dakota's full-stack work"
- "What's Dakota's experience with vector databases?"
- "Walk me through the Ben AI chatbot architecture"
- "Can Dakota work with [tech stack]?"

---

## Update Workflow (During Job Search)

When updating content:
1. Edit `data/resume.json` or create new project markdown file
2. Run embedding update script to re-index Qdrant (Phase 3+)
3. Test locally to ensure changes reflected
4. Deploy updates (should be < 5 minutes end-to-end)

**DO NOT** require complex rebuild processes for content updates.

---

## Success Metrics

**Technical:**
- - RAG retrieval accuracy (returns relevant projects for skill queries)
- - Response time < 3 seconds for typical queries
- - Multimodal responses work smoothly (images load quickly)
- - WebSocket connection stability (minimal fallback to REST)

**User Experience:**
- - Recruiters spend 2-5 minutes exploring vs 30 seconds on traditional resume
- - Positive feedback on uniqueness/innovation
- - Generates interview conversations about technical implementation

**Deployment:**
- - 99%+ uptime
- - Works on mobile devices
- - Fast page load (< 2 seconds)

---

## Notes & Reminders

- This is a **portfolio piece** as much as a functional tool - prioritize showcasing technical skills
- Keep it **professional** but inject personality (Dakota's voice should come through)
- **Document the build process** - could become a blog post or case study
- Consider adding a "How this was built" explainer section in the UI
- Monitor costs closely (should be < $10/month with free tiers)

---

## Current Phase: **Phase 1 - Foundation & Data Structure**

**Next Steps:**
1. Create project folder structure
2. Define and populate resume.json with Dakota's real data
3. Write 2-3 sample project markdown files
4. Set up requirements.txt

**DO NOT proceed to Phase 2 until Phase 1 is complete and reviewed.**
