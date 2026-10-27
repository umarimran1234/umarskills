# umarskills

A collection of Claude skills by [@umarimran1234](https://github.com/umarimran1234).

## Skills

| Skill | What it does |
|---|---|
| [`reel-video-pipeline`](reel-video-pipeline/SKILL.md) | Makes a voiced Instagram reel end to end: script, ElevenLabs voice-over, word-synced captions, paper-note or typography visuals, optional cartoon avatar with lip-sync, synthesized music, and an Instagram-safe mp4 (1080x1920, H.264, AAC 48 kHz stereo, faststart). |

## Requirements for `reel-video-pipeline`
- Claude with a workspace that can run Python, Node, ffmpeg and Playwright (Chromium).
- The ElevenLabs connector (spends your ElevenLabs credits for the voice-over).
- Network access to `storage.googleapis.com` so the generated audio can be downloaded.

## Install
**Claude (web/desktop):** zip the skill folder (for example `reel-video-pipeline`) and upload it under Settings -> Skills.

**Claude Code:** copy the folder to `~/.claude/skills/<skill-name>/` (or `.claude/skills/` inside a project).

## Use
Ask Claude for a reel, for example:

> Make a 35-second typography reel about how SaaS building changed. Use my ElevenLabs voice, end with "comment GUIDE".

## Notes
- Do not claim facts, offers or testimonials that are not true.
- Cold DMs violate Instagram policy. Use comment-to-DM funnels, which only reply to people who commented.

## License
MIT. See `LICENSE`.
