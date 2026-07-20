#!/bin/bash

echo "Starting backend..."
uvicorn app:app --reload &

echo "Starting frontend..."
cd frontend
npm run dev -- --open