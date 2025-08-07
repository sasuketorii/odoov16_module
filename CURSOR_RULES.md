# Cursor Rules for Odoo16-0805

## Scope
- Odoo 16 custom modules in `addons/`
- Japan localization priority, non-intrusive to core modules

## File/Folder Naming
- Files/Folders: kebab-case
- Classes: UpperCamelCase
- Functions: lowerCamelCase (start with verb)
- Variables: lowerCamelCase
- Constants: UPPER_SNAKE_CASE

## Formatting
- Encoding: UTF-8
- Indent: 2 spaces
- Semicolons: required in JS/SCSS where applicable
- Max line length: 80 chars
- Line endings: LF, ensure single trailing newline
- Trim trailing spaces

## Python Style
- Follow PEP 8
- Explicit imports from `odoo` APIs
- Prefer early returns; handle errors with exceptions
- Docstrings: Japanese, concise
- Avoid dead code and unused vars

## Odoo Module Rules
- Minimize `depends` in `__manifest__.py`
- Never change semantics of core fields; add fields or computed fields
- View inheritance uses `position` with smallest diff
- Translations in `i18n/ja.po`
- Access rules defined in `security/ir.model.access.csv`
- Keep module icons in `static/description/`

## Japan Localization
- Dates: YYYY/MM/DD or YYYY年MM月DD日
- Currency: JPY, no decimals
- Names: 姓→名、カナ必須箇所は半角カナ
- Address: 郵便番号→都道府県→市区町村→番地
- Errors and help texts in Japanese

## Git/CI
- Conventional Commits + Japanese imperative at start
- Keep SemVer in manifests
- Write tests; target coverage ≥ 80%
- Run linters in CI; resolve all warnings

## Secrets
- Use env vars; add `.env` to `.gitignore`

## Terminal Commands Policy
- Provide full, step-by-step commands with absolute paths and working dir

## Dev Shortcuts
- Update module list:
  ```bash
  cd /Users/sasuketorii/Odoo16-0805
  docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf --update-list
  ```
- Install a module:
  ```bash
  cd /Users/sasuketorii/Odoo16-0805
  docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf -i MODULE --stop-after-init
  ```
- Upgrade a module:
  ```bash
  cd /Users/sasuketorii/Odoo16-0805
  docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf -u MODULE --stop-after-init
  ```

## Review Checklist
- Manifest, security, views, data, i18n present
- No core breakage; uninstallable cleanly
- Logs free of errors/warnings
- Forms: labels/help in Japanese; kana fields auto-convert to half-width

## JS/CSS
- Place JS in `static/src/js/`, SCSS in `static/src/scss/`
- Use 2-space indent, keep lines ≤ 80 chars

## Commit Message Template
- `feat: ～を追加する` / `fix: ～を修正する` / `docs: ～を更新する` など 