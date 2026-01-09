# Promptly Web

Next.js frontend for the AI Search Visibility Platform.

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local with your configuration
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
apps/web/
├── app/                        # App Router pages
│   ├── layout.tsx              # Root layout with SEO
│   ├── page.tsx                # Landing page
│   ├── globals.css             # Global styles
│   │
│   ├── login/                  # Authentication pages
│   │   ├── layout.tsx          # Page metadata
│   │   └── page.tsx            # Login form
│   │
│   ├── register/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── verify/
│   │   └── [token]/
│   │       └── page.tsx        # Email verification
│   │
│   ├── dashboard/              # Protected area
│   │   └── page.tsx            # User dashboard
│   │
│   └── analysis/               # Analysis workflow
│       ├── new/
│       │   └── page.tsx        # Create analysis
│       └── [id]/
│           └── page.tsx        # View analysis
│
├── components/                 # React components
│   ├── Navigation.tsx          # Top navigation bar
│   ├── ErrorToast.tsx          # Toast notifications
│   ├── loading-skeleton.tsx    # Loading states
│   ├── empty-state.tsx         # Empty states
│   ├── accessibility.tsx       # A11y utilities
│   │
│   ├── analysis/               # Analysis components
│   │   ├── BrandEntryStep.tsx
│   │   ├── CompetitorSelectionStep.tsx
│   │   ├── PromptSelectionStep.tsx
│   │   ├── ProviderStatusCard.tsx
│   │   ├── AnalysisProgressBar.tsx
│   │   ├── ResponseList.tsx
│   │   ├── ResponseViewer.tsx
│   │   ├── CitationCard.tsx
│   │   ├── CitationModal.tsx
│   │   ├── ConfidenceBadge.tsx
│   │   ├── ProviderComparison.tsx
│   │   └── ProviderCapabilityIndicator.tsx
│   │
│   └── insights/               # Insights components
│       ├── VisibilityScoreDisplay.tsx
│       ├── SentimentIndicator.tsx
│       ├── ThemesGapsSection.tsx
│       ├── RecommendationsList.tsx
│       ├── BrandComparisonChart.tsx
│       ├── InsightCard.tsx
│       └── EvidenceModal.tsx
│
├── lib/                        # Utilities
│   ├── api-client.ts           # API wrapper with auth
│   ├── auth-api.ts             # Auth-specific API calls
│   ├── auth-context.tsx        # Auth state provider
│   ├── form-validation.ts      # Form validation utils
│   └── sse-client.ts           # SSE streaming client
│
├── public/                     # Static assets
│   ├── favicon.ico
│   └── og-image.png
│
├── tailwind.config.ts          # Tailwind configuration
├── next.config.ts              # Next.js configuration
├── tsconfig.json               # TypeScript config
└── package.json
```

## Components

### Loading Skeletons

```tsx
import {
  SkeletonCard,
  SkeletonAnalysisList,
  SkeletonDashboard
} from "@/components/loading-skeleton";

// Full page skeleton
<SkeletonDashboard />

// Individual components
<SkeletonCard />
<SkeletonAnalysisList count={5} />
```

### Empty States

```tsx
import {
  EmptyAnalyses,
  EmptyResults,
  EmptyInsights
} from "@/components/empty-state";

// No analyses
<EmptyAnalyses onStartAnalysis={() => router.push("/analysis/new")} />

// No search results
<EmptyResults searchTerm={query} onClear={() => setQuery("")} />
```

### Accessibility

```tsx
import {
  SkipToContent,
  ScreenReaderOnly,
  useAnnouncement
} from "@/components/accessibility";

// Skip link (in layout)
<SkipToContent />

// Screen reader text
<ScreenReaderOnly>Additional context for screen readers</ScreenReaderOnly>

// Live announcements
const { announce } = useAnnouncement();
announce("Analysis complete", "polite");
```

## API Client

### Basic Usage

```tsx
import { apiClient } from "@/lib/api-client";

// GET request
const analyses = await apiClient.get<Analysis[]>("/api/v1/analyses");

// POST request
const newAnalysis = await apiClient.post<Analysis>("/api/v1/analyses", {
  brand_name: "Acme Corp",
  brand_domain: "acme.com",
});

// Error handling
try {
  await apiClient.post("/api/v1/analyses", data);
} catch (error) {
  if (error instanceof APIError) {
    console.error(error.message, error.statusCode);
  }
}
```

### Auth Context

```tsx
import { useAuth } from "@/lib/auth-context";

function MyComponent() {
  const { user, isLoading, login, logout, isAuthenticated } = useAuth();

  if (isLoading) return <SkeletonCard />;
  if (!isAuthenticated) return <Redirect to="/login" />;

  return <div>Welcome, {user?.email}</div>;
}
```

### SSE Streaming

```tsx
import { createSSEClient } from "@/lib/sse-client";

const client = createSSEClient(`/api/v1/analyses/${id}/stream`);

client.on("provider_start", (data) => {
  console.log(`${data.provider} started`);
});

client.on("provider_complete", (data) => {
  console.log(`${data.provider} complete:`, data.response);
});

client.on("analysis_complete", () => {
  console.log("All providers complete");
});

// Start streaming
client.connect();

// Cleanup
client.disconnect();
```

## Styling

### Brand Colors

Defined in `tailwind.config.ts`:

```ts
brand: {
  primary: "#6366f1",   // Indigo
  secondary: "#8b5cf6", // Purple
  accent: "#06b6d4",    // Cyan
  dark: "#0f172a",      // Slate-900
  light: "#f1f5f9",     // Slate-100
}
```

### Responsive Breakpoints

| Breakpoint | Width | Use Case |
|------------|-------|----------|
| `xs` | 475px | Large phones |
| `sm` | 640px | Tablets (portrait) |
| `md` | 768px | Tablets (landscape) |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large desktops |
| `3xl` | 1920px | Full HD+ |

### Custom Animations

```tsx
// Fade in
<div className="animate-fade-in">...</div>

// Slide up
<div className="animate-slide-up">...</div>

// Slow pulse
<div className="animate-pulse-slow">...</div>
```

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- ComponentName
```

## Code Quality

```bash
# Lint
npm run lint

# Type check
npm run type-check

# Format (if Prettier configured)
npm run format
```

## Build

```bash
# Production build
npm run build

# Start production server
npm start

# Export static site (if applicable)
npm run export
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_SITE_URL` | Site URL for SEO | No |

## Key Patterns

### Protected Routes

Use the auth context to check authentication:

```tsx
"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ProtectedPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) return <SkeletonDashboard />;
  if (!isAuthenticated) return null;

  return <div>Protected content</div>;
}
```

### Form Validation

```tsx
import { validateRegistrationForm, getFieldError } from "@/lib/form-validation";

const errors = validateRegistrationForm(formData);
const emailError = getFieldError(errors, "email");
```

### Error Handling

```tsx
import ErrorToast, { SuccessToast } from "@/components/ErrorToast";

// In component
{errorMessage && (
  <ErrorToast
    message={errorMessage}
    onClose={() => setErrorMessage(null)}
  />
)}

{successMessage && (
  <SuccessToast
    message={successMessage}
    onClose={() => setSuccessMessage(null)}
  />
)}
```
