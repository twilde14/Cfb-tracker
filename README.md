# CFB Watch Planner (self-updating)

A pick-your-games college football planner. Game times, TV channels,
rankings, and spreads refresh automatically once a day. Anyone with the
link can pick their own games — picks are saved in each person's own
browser, not shared between people.

## One-time setup (~10 minutes)

1. **Create a GitHub account** if you don't have one: github.com/join (free).

2. **Create a new repository**
   - Click the "+" in the top right → "New repository"
   - Name it something like `cfb-watch-planner`
   - Make it **Public** (required for free GitHub Pages)
   - Click "Create repository"

3. **Upload these files**, keeping the folder structure intact:
   - `index.html`
   - `data.json`
   - `scripts/update_data.py`
   - `.github/workflows/update.yml`
   - `README.md` (optional, just for reference)

   Easiest way: on your new repo's page, click "Add file" → "Upload files",
   then drag the whole extracted folder in from Finder/Explorer — GitHub
   preserves the subfolders when you drag a folder in (not when you use
   the file picker, so drag-and-drop is the reliable way).

4. **Turn on write permissions for the automation**
   - Go to your repo's **Settings** → **Actions** → **General**
   - Scroll to "Workflow permissions"
   - Select **"Read and write permissions"**
   - Click **Save**

5. **Turn on GitHub Pages**
   - Go to **Settings** → **Pages**
   - Under "Source," choose **"Deploy from a branch"**
   - Branch: **main**, folder: **/ (root)**
   - Click **Save**
   - GitHub will give you a URL like `https://yourusername.github.io/cfb-watch-planner/`
     (it can take a minute or two to go live the first time)

6. **Run the update once manually** so it's not empty on day one
   - Go to the **Actions** tab
   - Click **"Update CFB schedule data"** in the left sidebar
   - Click **"Run workflow"** → **"Run workflow"**
   - Wait ~30 seconds, refresh, and you should see a green checkmark
   - Your site now has real data

That's it — from here it re-runs automatically every day at 7am Mountain
and commits any changes. Just share the `github.io` link with people.

## If something breaks

This pulls from an undocumented ESPN endpoint (there's no clean official
free API for schedule + TV + odds together). If ESPN changes their data
format, the daily run may start failing or come back with fewer games.
Check the **Actions** tab — a red X means the last run failed, and the
log will show why. Bring it back to me and I can help patch the script.

## Customizing

- **Change the refresh time/frequency:** edit the `cron` line in
  `.github/workflows/update.yml`. It's in UTC.
- **Change how many days ahead it pulls:** edit `DAYS_AHEAD` in
  `scripts/update_data.py`.
- **Add FCS-only or other filters:** the `GROUPS` list in the same file
  controls which divisions get pulled (`80` = FBS, `81` = FCS).
