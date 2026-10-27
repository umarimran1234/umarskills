---
name: "reel-video-pipeline"
description: "Make a voiced Instagram reel (script, ElevenLabs voice, synced captions, avatar or typography, music, IG-safe mp4) end to end in the workspace. Use for any reel/short video request."
---

# Reel video pipeline (Claude + ElevenLabs)

Builds a 25-45s vertical (1080x1920, 30fps) reel: Roman Urdu/English voice-over from ElevenLabs, word-synced captions, paper-note / typography visuals, optional cartoon avatar with lip-sync, optional screen recording, synthesized music, and an Instagram-safe mp4.

The user usually writes Roman Urdu mixed with English tech words and wants fast, direct replies. Match that.

## 0. Inputs to settle (ask at most one short question, otherwise decide)
- **Topic + promise** (what the viewer gets) and **CTA** (e.g. "comment GUIDE" -> DM).
- **Style**: (a) *typography* (big animated words + paper notes, no screen recording), (b) *screen-recording* (product demo inside a bezel card), (c) both. If the topic is not the user's product, never show the product recording. Default to typography for informational reels.
- **Voice**: ElevenLabs voice id (user-chosen; the "Bunty - Reel Perfect Voice" id was FZkK3TvQ0pjyDmT8fzIW). Otherwise `creative_list_voices` and pick a clear natural one; say which.
- **Avatar**: yes/no. **Real face video** requests are a different job (give script + shot list, then edit their footage).
- Facts: never invent stats, testimonials or features. Claims must be true or hedged ("reports ke mutabiq"). Do not promise a guide/offer that does not exist; offer to create it.

## 1. Script rules
- 6 beats, 30-40s. Spoken pace is about 2.5 Roman Urdu words/second. 85-110 words total.
- Beat order: hook (problem, 3-5s) -> what changed / the tool -> how it works (3 steps) -> twist or proof -> why it matters -> CTA.
- Natural spoken Roman Urdu, short sentences, few ellipses. Too many "..." and `[excited]` tags make the voice sound artificial; use at most one tag, or none for calm explainers.
- Put the offer (e.g. FREE) where the user wants it. Keep keywords the viewer must comment in caps once.
- Output also: caption, hashtags (5 famous + niche mix, put in first comment after `.` lines), pinned comment.

## 2. Voice with ElevenLabs (costs credits)
Tools: `mcp__ElevenLabs__creative_generate_speech`, `creative_get_flow_run_status` (may be deferred; load via ToolSearch `select:`).
- `model_id: eleven_v4`, `voice_id`, `generations_count: 1`, prompt = whole script, one paragraph per beat.
- **Never call generate twice to retry** (it charges again). A 429 rate_limit error means nothing started; wait, tell the user, retry only when they say so.
- Optional `estimate_only: true` first when the user is credit-sensitive. Typical cost 580-680 credits for 35-40s.
- Poll `creative_get_flow_run_status(flow_id, session_ids)` every few seconds until `all_completed`. Use a Monitor/short wait, not chained sleeps.
- Download `content_url` with `curl -o voX/full.mp3 "<url>"` (the host storage.googleapis.com must be allowed in the user's network settings; if the proxy returns 403, tell the user to allow the domain; never bypass). Then `ffmpeg -ar 24000 -ac 1 full.wav`.
- Share the flow link with the user (flow_url) and mention credits used.

## 3. Word alignment (voice -> timeline)
No transcription tool needed. Detect speech segments with silencedetect, then assign script words to segments by dynamic programming weighted by character counts:
```python
err=subprocess.run(["ffmpeg","-i","vo/full.wav","-af","silencedetect=noise=-34dB:d=0.14","-f","null","-"],capture_output=True,text=True).stderr
ss=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",err)]; se=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",err)]
segs=[];cur=0.0
for a,b in zip(ss,se):
    if a-cur>0.08: segs.append((cur,a))
    cur=b
if DUR-0.08-cur>0.1: segs.append((cur,DUR-0.08))
ch=np.array([len(re.sub(r'\W','',w))+1+(2 if re.search(r'[.!?,]$',w) else 0) for w in tok],float)
rate=ch.sum()/sum(e-s for s,e in segs)
# dp[k][j]: first j words in first k segments; cost=((chars in group)-(seg_dur*rate))**2 (+6 if empty)
# backtrack -> groups; inside a segment split time proportional to chars
```
Output `timeline_new.json`: `words:[{w,s,e,b}]`, `bs` (beat start = first word start of beat, minus 0.12; beat 0 = 0), `beats`, `dur = voice_len + 0.9`, and an anchor dict `A` of named times from `find(norm_word, nth)` (normalize with `re.sub(r'\W','',w).lower()`). Use anchors (not hard-coded seconds) to time every on-screen element. Verify by printing `word@time` and checking the order.

## 4. Mouth envelope for the avatar (30fps)
```python
x=np.frombuffer(wave.open('vo/full.wav').readframes(n),np.int16).astype(float)
r=np.array([np.sqrt(np.mean(x[int(i/30*sr):int((i+1)/30*sr)]**2)+1e-9) for i in range(int(dur*30))])
r=np.nan_to_num(r); r=np.clip(r/np.percentile(r,92),0,1)**0.8; r=np.convolve(r,[.25,.5,.25],'same')
open('mouth.js','w').write('window.MOUTH='+json.dumps([round(float(v),3) for v in r])+';')
```
Scene: `mouthOpen.setAttribute('transform','scale(1 '+open+')')` with `open=clamp(MOUTH[round(t*30)]*1.05+0.04)`; smile hidden when open>0.2; blink every 2.4s; head bob `sin(t*6)*4`, tilt `sin(t*3.1)*3`; arm points on emphasis beats. Guard NaN/undefined.

## 5. Scene (single HTML, 1080x1920, deterministic `render(t)`)
Layout zones: top 70-570 paper note (one at a time), middle 640-1240 typography stage (or bezel card + green `#00ff00` hole for screen recording), bottom-left avatar (left -30, top 1400, scale .72), lower-right sticky notes / CTA card (x>=330 to avoid the avatar), captions at ~y1288 (hide them when typography stage is used). Keep important things out of the bottom ~270px (Instagram UI) except the avatar body.
- Fonts: Permanent Marker (headings), Caveat/Patrick Hand (notes) from local @fontsource files; check `fonts/` before using, no network.
- Elements table `E=[id, at, until, rotation, [dx,dy,drot]]` with times from anchors; entry uses back-ease (`eob`), exit fade 0.35s.
- Caption/stage chunks: group words into <=3 per chunk, break at punctuation; show words progressively (opacity/translate/scale pop), highlight current word yellow, keywords coral (`/saas|ai|users|guide|.../`).
- `render(t)` must be pure (set styles from t). Embed timeline via `__TL__` replace -> `scene_built.html`.
- Preview: Playwright screenshots at 6-10 key times, make a contact sheet, read it, fix overflow (long text -> smaller font), overlaps, and clipped right-edge cards before the full render.

## 6. Optional screen-recording b-roll
Only for the user's own product demos. Crop/zoom the recording to 1040x620 per beat (keyframed crops, cap crop width so the taskbar never shows, hold last frame instead of stretching) using ffmpeg raw frames + PIL, into `screen.mp4`. Composite later by `colorkey=0x00ff00:0.32:0.1` over `pad=1080:1920:20:620`. Not needed for typography style.

## 7. Render frames (parallel) - run in background
```python
# render_frames.py a b
pg=br.new_page(viewport={"width":1080,"height":1920}); pg.goto("file:///.../scene_built.html"); pg.wait_for_timeout(600)
for i in range(a,b): pg.evaluate(f"render({i/30})"); pg.screenshot(path=f"frames/f_{i:04d}.jpg",type="jpeg",quality=92)
```
Split N=dur*30 frames into 4 processes (`&` then `wait`). 1100 frames take roughly 5-8 min. Run the whole build script with `run_in_background`, then watch with Monitor on a `FINISHED` marker in a log file. **Do not** use `pgrep -f render_frames` in a Monitor loop (it matches itself and never ends).

## 8. Music (synthesized, no downloads)
numpy track at 124 bpm: kick, snare after the first beat, hats, A-minor pluck arpeggio, bass; whoosh + pop at each beat start and at anchors; final pop run on the CTA word; fade out 0.8s; `tanh` + normalize to 0.8. Duration = timeline dur.

## 9. Composite + mix + IG-safe export
```bash
ffmpeg -y -framerate 30 -i frames/f_%04d.jpg [-i screen.mp4 -filter_complex "[0:v]colorkey=0x00ff00:0.32:0.1[fg];[1:v]pad=1080:1920:20:620:black[sc];[sc][fg]overlay=0:0:shortest=1[v]" -map "[v]"] -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 17 -preset fast nov.mp4
ffmpeg -y -i nov.mp4 -i vo/full.wav -i music.wav -filter_complex "[1:a]apad,volume=1.25,asplit=2[v][sc];[2:a]volume=0.55[m];[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=250[md];[v][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,aresample=48000,aformat=channel_layouts=stereo[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t DUR out.mp4
```
Instagram-safe means: H.264 High, yuv420p, 30fps, AAC **48kHz stereo**, `+faststart`. (A 24kHz mono file without faststart caused upload/playback problems.)

## 10. QA before sending
- `ffprobe`: video/audio streams exist, durations match, sample_rate 48000, channels 2.
- Extract 2-3 frames with ffmpeg and look at them (hook, middle, CTA); check word sync on a few captions.
- Check notes do not cover the avatar or overflow the edges; CTA card fully inside 1080px.
- Send with `SendUserFile` (display render) and give: what changed, credits used + flow link, caption/hashtags, claims to verify, and the next step.

## 11. Lead-magnet reels (comment GUIDE -> DM)
If the CTA promises a guide: confirm it exists or create it (HTML -> Playwright `page.pdf`, A4, Inter + Permanent Marker, ~10 pages, no invented stats). Tell the user to host the PDF (Drive link) and set a comment-to-DM automation for the keyword. Remind: cold DMs violate Instagram policy; only reply to people who commented/messaged.

## Pitfalls
- Free-tier/account errors from ElevenLabs: tell the user which account issue; do not retry blindly.
- Overlong text in notes: shrink font before rendering 1000+ frames.
- Keep timing anchors unique: some words repeat (`find(word, nth)`); verify indexes by printing times.
- Do not use real brand/character likenesses for the avatar; it is an original cartoon.
- If a topic needs fresh facts (stats, current tools), search first and hedge unverified numbers in the voice-over.