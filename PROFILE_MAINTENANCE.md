# Profile maintenance

The README is the public profile. All artwork is original, standalone SVG in `assets/`. No game sprites, captures, credentials or private source files are included.

- Edit `README.md` for the introduction and links.
- Edit `assets/header.svg` for the banner, `assets/now.svg` for rotating phrases, or a project SVG for its card.
- Motion groups respect reduced-motion preferences. Essential text and icons remain visible.
- The workflow refreshes `assets/activity.svg` daily using public repository metadata. No personal access token is needed.
- Totals exclude forks and the profile repository. Language counts measure repositories, not lines of code.
- Profile changes and manual workflow runs render a static contact sheet for review in the workflow log.
- Run `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_profile.py` before publishing edits.

The portfolio remains separate and private at `BuildWithRaymond/BuildWithRaymond-portfolio`. Update any existing portfolio clones or deployment integrations to that URL. The original name now belongs to this profile.
