# Quote Video Generator

A small desktop app for turning a reference image plus a written quote into a short narrated video clip, using Google's Gemini Omni Flash image-to-video model.

Built with Python's built-in `tkinter`, so there's no browser, no server, and no environment variables to configure — just a window with fields.

## Features

- Pick a reference image once, generate a new clip per quote
- Live image preview before generating
- API key entered in-app and held in memory only (never written to disk)
- Aspect ratio (16:9 / 9:16) and resolution (720p / 1080p / 4K) selection
- Cost estimate shown per resolution tier
- Confirmation prompt before the more expensive 1080p and 4K generations
- Runs generation on a background thread so the window stays responsive
- Save-as dialog for the finished `.mp4`

## Requirements

- Python 3.9 or newer
- A Gemini API key from [Google AI Studio](https://aistudio.google.com)

## Installation

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
pip install -r requirements.txt
```

On Windows, if `python` isn't recognized, use `py` instead.

## Usage

```bash
python quote_video_app.py
```

Then in the window:

1. Paste your Gemini API key
2. Click **Choose image...** and select your reference image
3. Type the quote you want narrated
4. Optionally add extra direction (tone, camera movement, audio style)
5. Pick aspect ratio and resolution
6. Click **Generate video** and choose where to save the result

Start at 720p to confirm everything works before spending on higher tiers.

## Cost

Generation is billed per second of output video. At the time of writing, 720p runs roughly $0.10/sec, so a short clip typically lands under $1. 1080p and 4K cost more due to upscaling. Check Google's current pricing page before running large batches — rates change.

## Troubleshooting

**`ValueError: No API key was provided`**
You're running an older version of the script that read the key from an environment variable. Make sure you're running the current `quote_video_app.py` from this repo.

**`content_blocked` / "Input blocked ... guardrails related to third-party content"**
Google's safety classifier rejected the input before generation. This is enforced server-side and can't be bypassed from the client. Common triggers include recognizable real people, brand logos, stock-photo watermarks, and copyrighted artwork. Try a cleaner reference image to isolate which element is being flagged. If a fully original asset is still blocked, report it via the feedback link in the error message.

**`ModuleNotFoundError: No module named 'PIL'`**
Run `pip install pillow`.

**Nothing happens / no window appears**
On some minimal Linux installs, `tkinter` isn't bundled. Install it with your package manager (e.g. `sudo apt install python3-tk`).

## Security note

Your API key is never stored by this app — it lives only in the input field for the duration of the session. Don't hardcode a key into the source, and don't commit one. If a key is ever exposed, revoke it in Google AI Studio immediately; keys that reach git history remain recoverable even after later commits remove them.

## License

MIT — see [LICENSE](LICENSE).
