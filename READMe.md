# MAYA: An AI Co-Presenter for Real-Time Presentation Assistant

A next-generation real-time AI system for controlling presentations, identifying speakers, responding intelligently, and acting as a live co-presenter.

---

## Author / Maintainer

**Name:** Subham Chaudhary <br>
**Email:** [shubhu.uwu@gmail.com](mailto:shubhu.uwu@gmail.com) <br>
**Team_ID:** 8
---


## Project Overview

This project aims to build a full real-time AI Co-Presenter capable of:

* Listening to live microphone audio
* Performing speech-to-text through Murf ASR (Streaming)
* Detecting speaker boundaries (diarization)
* Identifying specific speakers using embeddings stored in PostgreSQL + pgvector
* Understanding context through an LLM with function calling
* Controlling a live PowerPoint presentation (via Windows COM API / pywin32)
* Generating natural speech in real time using Murf TTS
* Working with sub-second latency (< 1 second end-to-end)

This is a modular and scalable system designed to run locally on Windows and integrate tightly with presentation tools. (Its still in development)

---

## Core Modules (High-Level)

* Audio Streaming Module – Live mic streaming, chunking, VAD
* Speech Diarization Module – Detect speaker boundaries
* Speaker Identification Module – Compare embeddings via pgvector
* ASR Module (Murf API) – Real-time transcription
* LLM Reasoning Engine – Function-calling to decide slide actions
* Presentation Parsing Module – Extract layout data using python-pptx
* Live Presentation Controller – Control PowerPoint using COM automation
* TTS Module (Murf TTS) – Generate co-presenter audio
* Server Orchestrator – FastAPI backend connecting all modules

A detailed folder structure will be added once the repository is finalized.

---

## Tech Stack / Tools Used

### Languages

* Python 3.10+

### AI / ML

* pyannote.audio (diarization)
* ECAPA-TDNN / Speaker Embeddings
* LLM (Ollama / Gemini / OpenAI) with function-calling (Whatever seems best, I'll create a module to easily switch between them)
* Murf API – Streaming ASR + TTS

### Databases

* PostgreSQL 16
* pgvector (for storing voice embeddings)

### Presentation Tools

* python-pptx
* pywin32 (PowerPoint COM interface)

### Backend

* Flask
* Gunicorn
* Uvicorn

---

### This project is tightly build for the upcoming TechFest for IIT Bombay (2025).
---

## Summary of What This System Does

This project builds a fully automated real-time AI co-presenter that can:

* Listen to you during a presentation
* Detect who is speaking
* Understand slide context
* Navigate slides intelligently
* Highlight and zoom into elements
* Provide co-presenter speech when needed
* Respond naturally using an LLM
* Maintain under 1-second latency for live interactions

The system integrates audio streaming, speaker recognition, LLM reasoning, and presentation control into a single orchestrated pipeline, creating an intelligent assistant capable of controlling a live presentation based on voice cues.

---
### Contact me for any quieries or suggestions (same goes for judges)

### soon upload the demo video here