# Required Permissions for Viability Check Experiment

## API Keys Needed (FREE TIER ONLY)

To run the viability check experiment, you need API keys from the following **FREE** providers:

### 1. Groq (FREE)
- **Models:**
  - `llama-3.3-70b-versatile` (newest, best reasoning)
  - `llama-3.1-70b-versatile` (stable)
- **Cost:** **FREE** (generous free tier)
- **Rate limits:** 30 requests/min, 6K requests/day (we send ~7 req/min)
- **How to get:**
  1. Sign up at https://console.groq.com/
  2. Generate API key under API Keys
  3. Export: `export GROQ_API_KEY="gsk_..."`

### 2. Google Gemini (FREE)
- **Models:**
  - `gemini-2.0-flash-exp` (experimental, better reasoning)
  - `gemini-1.5-flash` (stable)
- **Cost:** **FREE** (15 RPM, 1M tokens/day free tier)
- **How to get:**
  1. Sign up at https://aistudio.google.com/
  2. Generate API key
  3. Export: `export GOOGLE_API_KEY="..."`

## Total Estimated Cost

**$0** - Completely free!

## Setting API Keys

### Option 1: Environment Variables (Recommended)

```bash
# Add to your ~/.bashrc or ~/.zshrc
export GROQ_API_KEY="gsk_..."
export GOOGLE_API_KEY="..."
```

### Option 2: .env File (Local Only)

```bash
# Create .env file in project root (already gitignored)
echo 'GROQ_API_KEY="gsk_..."' >> .env
echo 'GOOGLE_API_KEY="..."' >> .env

# Load with python-dotenv (add to requirements.txt if needed)
pip install python-dotenv
```

## Rate Limits

The experiment script includes delays between requests to respect free tier rate limits:

- **Groq:** 30 requests/min (free tier) - we send ~7 req/min with 2s delays
- **Google:** 15 requests/min (free tier) - we send ~7 req/min with 1s delays

All well within limits. The experiment will be slower but completely free!

## Running Without All Keys

The experiment will skip any provider for which an API key is not found:

```bash
# Run with only Groq
export GROQ_API_KEY="gsk_..."
python run_experiment.py  # Skips Google

# Run with both (recommended)
export GROQ_API_KEY="gsk_..."
export GOOGLE_API_KEY="..."
python run_experiment.py
```

## Permissions Granted

Please grant permission to run the following background commands:

```bash
# 1. Generate the problem dataset
python curate_problems.py

# 2. Run the experiment (makes API calls)
python run_experiment.py

# 3. Analyze results (local only, no API calls)
python analyze_results.py
```

These commands will:
- Read/write local files in `experiments/viability_check_1/`
- Make API calls to LLM providers (if keys are set)
- NOT modify any source code
- NOT access any files outside the experiment directory
