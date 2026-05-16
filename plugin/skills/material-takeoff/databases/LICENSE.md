# Bundled database attributions

## oekobaudat-en.json

Source: **ÖKOBAUDAT** — published by the German Federal Ministry for Housing, Urban Development and Building (BMWSB) at <https://www.oekobaudat.de>.

Licence: **Creative Commons Attribution 4.0 International (CC BY 4.0)** — <https://creativecommons.org/licenses/by/4.0/>.

The data in `oekobaudat-en.json` is a translated, structurally-normalised snapshot of the ÖKOBAUDAT dataset, processed through <https://github.com/nio-energy/nio-lca-databases>. Original life-cycle assessment values are unmodified.

When this database is used to produce a material take-off, the Excel output cites the matched record's `Conformity` and `Url` in the Matches sheet — that constitutes the required attribution.

## ICE.json

Source: **Inventory of Carbon and Energy (ICE) Database** — University of Bath / Circular Ecology, <https://circularecology.com>.

Licence: **Free for non-commercial use; commercial use requires a separate licence from Circular Ecology.**

The ICE database is bundled for reference and validation only. **Do not use ICE matches in commercial deliverables without obtaining a commercial licence from Circular Ecology first.** The plugin's default workflow matches against ÖKOBAUDAT and treats ICE as a secondary cross-check.

Original ICE records are unmodified, processed through <https://github.com/nio-energy/ICE2json> for structural normalisation only.
