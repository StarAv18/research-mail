# Vercel Deployment Guide - Research Internship Agent

This guide provides instructions for deploying the frontend of the Research Internship Agent to Vercel.

## Prerequisites

- A Vercel account.
- GitHub/GitLab/Bitbucket repository connected to Vercel.
- Backend API deployed and accessible (e.g., on Render, Railway, or AWS).

## Deployment Steps

1. **Connect Repository**:
   - In the Vercel dashboard, click **New Project**.
   - Import the repository containing the `frontend` folder.

2. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

3. **Environment Variables**:
   Add the following environment variables in the Vercel project settings:

   | Name | Value | Description |
   |------|-------|-------------|
   | `NEXT_PUBLIC_API_URL` | `https://your-backend-api.com/api/v1` | Base URL of your production API |

4. **Deploy**:
   - Click **Deploy**. Vercel will build and host your application.

## Local Verification

Before pushing changes, ensure everything works locally:

```bash
cd frontend
npm install
npm run lint
npm run build
```

## Troubleshooting

- **Build Failures**: Ensure all TypeScript errors are resolved. Run `npm run build` locally to catch them.
- **API Issues**: Verify `NEXT_PUBLIC_API_URL` is correctly set and includes the protocol (`https://`) and version suffix (`/api/v1`).
- **CORS Errors**: Ensure your backend API allows requests from your Vercel deployment domain.
