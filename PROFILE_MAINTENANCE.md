# Profile maintenance

The README is the public profile. Artwork is standalone SVG in `assets/`, including the supplied Hernbrode identity. No game sprites, captures, credentials or private source files are included.

- Edit `README.md` for the introduction and links.
- Static artwork is generated manually by `scripts/render_brand_assets.py`. Update its layout/copy, then regenerate instead of editing output that a later manual run will overwrite. From the Agency workspace, run `python github-profile/scripts/render_brand_assets.py --brand-dir public/brand`; from another checkout, pass the directory containing the approved identity files.
- The exact supplied Hernbrode wordmark and H monogram belong to the owner's supplied identity. The generator copies the existing outlined geometry from `logo-cream.svg`, `mark-cream.svg`, and `mark-black.svg` without redrawing or replacing it. Supply those approved source files when regenerating; they are not fetched from another service.
- Header, mobile header, service strip, technology list, project artwork and closing artwork are static. No rotating phrases, motion groups, or animation dependencies are present.
- The workflow refreshes `assets/activity.svg` and `assets/activity-mobile.svg` daily from the same public repository summary and UTC date. Both generated files are committed together. No personal access token is needed.
- Totals exclude private repositories, records without confirmed public visibility, forks, and the profile repository. Language counts measure repositories, not lines of code. Stars are stars across those original public repositories, not client or business results.
- Keep activity rendering in the same brand system: ink `#0B0B0B`, charcoal `#1F1F1F`, cream `#F3EEE7`, restrained orange `#FF6A00`, and muted text `#BDB6AD`. Daily updates use `scripts/update_activity.py`; editing only the generated SVGs will be overwritten. The 480 px mobile variant uses at least 22 px labels and 64 px counts so it remains readable when GitHub scales it to a narrow article column. README `<picture>` selects the compact variant; the desktop contact sheet keeps the wide variant.
- Profile changes and manual workflow runs render a static contact sheet for review in the workflow log.
- The preview canvas height is calculated from all rendered assets, including the tallest card in each row. The existing `SVG_PREVIEW_BASE64:` log output is preserved. To also save a local PNG, run `python3 scripts/render_preview.py --output /tmp/profile-preview.png` in an environment with CairoSVG and Pillow. The workflow installs these dependencies on Ubuntu; Windows also needs Cairo's native runtime.
- Static artwork in the README is pinned to the published design commit `1be7830c88d28f64df956da0de2297adc847e529` so cached branch URLs cannot show a previous design. After a future artwork change, publish that artwork commit first, then update its static README image references to the new full commit SHA.
- Dynamic `activity.svg` and `activity-mobile.svg` references use the explicit `refs/heads/main` path so daily refreshes remain visible without changing a design pin. Keep these two activity references unpinned.
- README image sources may use relative `assets/...` paths or raw GitHub URLs belonging to this profile on `main`, `refs/heads/main`, or a full commit SHA. Other branches and external hosts are rejected. Validation checks every `<img>` and `<picture><source srcset>` candidate, resolves only files within local `assets/`, and never fetches remote resources.
- Run `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_profile.py` before publishing edits.

Keep upstream attribution for forked community projects. Do not publish private repository names, private implementation details, credentials, or unsupported business claims in this profile. A private portfolio remains separate from the public profile.

The intended website domain is omitted from public links until the owner confirms that the website is live and the destination is correct. Do not infer domain ownership or a working mailbox from the brand name.

