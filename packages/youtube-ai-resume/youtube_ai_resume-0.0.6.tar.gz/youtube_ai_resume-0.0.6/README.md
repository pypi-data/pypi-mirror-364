
# youtube-ai-resume

**Generate concise AI summaries of YouTube videos from the command line.**
It works in two steps:

1. Downloads the video caption (subtitles) with `pytubefix`.
2. Sends the caption to the OpenAI API and returns a summary in the language you choose.

<p align="center">
  <img src="https://img.shields.io/pypi/v/youtube-ai-resume?color=brightgreen" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/youtube-ai-resume" alt="Python Version">
  <img src="https://img.shields.io/github/license/your-user/youtube-ai-resume" alt="License">
</p>

---

## Features

* **Zero-setup CLI** → `youtube-ai-resume <video_id>`
* Summaries in any language (default `pt_BR`)
* Works with models like **`gpt-4.1-mini`** (configurable)
* Rich-formatted output with colours
* Usable as a *library* (`import youtube_ai_resume`)

---

## Installation

```bash
# Python ≥ 3.9
pip install youtube-ai-resume
```

Or, from source for development:

```bash
git clone https://github.com/fberbert/youtube-ai-resume.git
cd youtube-ai-resume
pip install -e ".[dev]"     # editable + dev tools
```

## Quick start

### Command Line Usage

```bash
export OPENAI_API_KEY="sk-..."
youtube-ai-resume dQw4w9WgXcQ     # Rick Astley demo 😄
```

Sample output:

```plaintext
Summary:

• Rick distances himself from breaking promises
• Emphasises commitment (“never gonna give you up…”) …
```
### Command Line Usage

```bash
export OPENAI_API_KEY="sk-..."
youtube-ai-resume 'https://www.youtube.com/watch?v=Ht2QW5PV-eY'
```

Sample output:

```plaintext
Summary:

The speaker, Dashish, an engineer on OpenAI’s product team, discusses advancements in AI agents that integrate improved models with powerful tools to 
enhance user experience. Key points include:

- **Symbiotic Improvement**: Better tools enable more capable AI agents, which in turn can utilize more powerful tools, creating a continuous cycle of 
enhancement.
- **Agent Capabilities**: The AI agent can access various personal tools and data sources, such as Gmail and Google Calendar, through connectors to perform
complex tasks.
- **Use Case - Booking a Tennis Tournament Itinerary**:
  - The agent is tasked with planning a detailed itinerary for a tennis tournament in Palm Springs, focusing on semi-final dates.
  - It checks the tournament schedule, the user’s calendar availability, flight options, hotel bookings, match attendance, and dining plans.
  - The agent uses a visual browser and personal data access to gather and coordinate all necessary information.
- **User Experience**: The agent automates the research and planning process, handling logistical details like travel time and meeting schedules, then 
notifies the user with a comprehensive plan to review.
- **Benefit**: This automation frees users from mundane tasks, allowing them to focus on the core activities they care about.

Overall, the presentation highlights how integrating AI models with personal data and external tools can create intelligent agents that manage complex, 
personalized planning tasks efficiently.
```

### Library usage

```python
from youtube_ai_resume import caption, summarizer

txt = caption.fetch_caption("dQw4w9WgXcQ")
summary = summarizer.summarize(
    transcript=txt,
    api_key="sk-…",
    model="gpt-4.1-mini",
    out_lang="pt_BR"
)
print(summary)
```

## Configuration


## Voice narration (Text-to-Speech) [Optional]

You can optionally have the summary narrated aloud using Google Cloud Text-to-Speech (TTS).

### Optional Requirements (only if you want voice narration)

- A Google Cloud account with the Text-to-Speech API enabled
- A service account key (JSON) with permission to use TTS
- The dependencies `google-cloud-texttospeech` and `playsound` (already included in requirements.txt)

### Optional Setup

1. Create a project in Google Cloud and enable the Text-to-Speech API.
2. Generate and download a service account credentials file (JSON).
3. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your credentials file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
```

Or authenticate using the Google Cloud CLI (`gcloud`):

```bash
gcloud auth application-default login
```

### Usage

- To hear the summary narration, add the `--voice` option to the command:

```bash
youtube-ai-resume dQw4w9WgXcQ --voice
```

- To enable narration by default, add to your config.json:

```json
{
    "voice_enabled": true
}
```

You can customize voice, language, and speed in config.json (see code examples).

---

You can set the OpenAI API key as an environment variable or in a config file.

Environment variable:

```bash
OPENAI_API_KEY="sk-..."
```

Config file at ~/.config/youtube-ai-resume/config.json (auto-created on first run) lets you change the default model.

```json
{
    "model": "gpt-4.1-mini",
    "out_lang": "en"
}
```

## Development

Contributions are welcome!

Fork ➜ branch ➜ PR.

ruff check . and pytest must pass.

Describe your change clearly.

## License

Released under the MIT License – see LICENSE.
