# TODO - HuggXet-Downloader

## 🔒 Private Submodule Setup (HIGH PRIORITY)

### Step 1: Create Private GitHub Repository
- [ ] Go to https://github.com/new
- [ ] Repository name: `HuggXet-Downloader-Internal`
- [ ] Description: "Internal documentation and agent instructions"
- [ ] Visibility: **Private** 🔒
- [ ] Do NOT initialize with README, .gitignore, or license
- [ ] Click "Create repository"

### Step 2: Initialize Private Repo with Instructions
```bash
cd .instructions
git init
git add AGENT_INSTRUCTIONS.md
git commit -m "Initial commit: Add agent instructions"
git remote add origin git@github.com:anonusername/HuggXet-Downloader-Internal.git
git branch -M main
git push -u origin main
cd ..
```

### Step 3: Remove Local Directory (Temporary)
```bash
rm -rf .instructions
```

### Step 4: Add as Submodule to Main Project
```bash
git submodule add git@github.com:anonusername/HuggXet-Downloader-Internal.git .instructions
```

### Step 5: Commit Submodule Reference
```bash
git add .gitmodules .instructions
git commit -m "Add internal instructions as private submodule"
git push origin the_path
```

### Step 6: Verify Setup
- [ ] Clone in new location to test: `git clone --recurse-submodules <repo-url>`
- [ ] Verify `.instructions/AGENT_INSTRUCTIONS.md` exists
- [ ] Test fork scenario (or ask someone to fork and verify empty `.instructions/`)

---

## 📱 Mobile Build Assets (OPTIONAL)

### Android Build Prerequisites
- [ ] Install buildozer: `pip install buildozer`
- [ ] Install Java JDK 8 or 11
- [ ] Install Android SDK and NDK (buildozer can auto-install)
- [ ] Windows users: Install WSL 2 with Ubuntu/Debian
- [ ] Test build: `buildozer android debug` (or via WSL)

### iOS Build Prerequisites (macOS only)
- [ ] Install briefcase: `pip install briefcase`
- [ ] Install Xcode from Mac App Store
- [ ] Install Xcode Command Line Tools: `xcode-select --install`
- [ ] Test build: `briefcase build ios`

### App Icons and Assets
- [ ] Create app icon: `resources/icon.png` (1024x1024 recommended)
- [ ] Create launch screen assets (if desired)
- [ ] Update `buildozer.spec` with icon path: `icon.filename = %(source.dir)s/resources/icon.png`
- [ ] Update `pyproject.toml` icon path: `icon = "resources/icon"`

### Android Signing (for Release Builds)
- [ ] Generate keystore: `keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000`
- [ ] Add keystore info to `buildozer.spec`:
  ```ini
  [app]
  android.release_keystore = /path/to/my-release-key.keystore
  android.release_keystore_passwd = your_password
  android.release_keyalias = my-key-alias
  android.release_keyalias_passwd = your_password
  ```
- [ ] **CRITICAL:** Add keystore to `.gitignore` (never commit signing keys!)

### iOS Signing (for App Store)
- [ ] Enroll in Apple Developer Program ($99/year)
- [ ] Create App ID in Apple Developer Portal
- [ ] Create provisioning profile
- [ ] Configure signing in Xcode
- [ ] Update `pyproject.toml` with bundle identifier

---

## 🔧 GitHub Integrations (OPTIONAL)

### GitHub Actions - CI/CD
- [ ] Create `.github/workflows/test.yml` for automated testing
- [ ] Configure Python version matrix (3.8, 3.9, 3.10, 3.11)
- [ ] Add coverage reporting
- [ ] Add badge to README.md: `![Tests](https://github.com/anonusername/HuggXet-Downloader/workflows/Test%20Suite/badge.svg)`

### Dependabot - Dependency Updates
- [ ] Create `.github/dependabot.yml`
- [ ] Configure weekly dependency checks
- [ ] Set up auto-merge for minor updates (optional)

### GitHub Codespaces
- [ ] Create `.devcontainer/devcontainer.json`
- [ ] Configure Python environment
- [ ] Test Codespace launch
- [ ] Add "Open in Codespaces" badge to README

### GitHub Projects
- [ ] Create project board for issue tracking
- [ ] Add labels: `bug`, `enhancement`, `documentation`, `mobile`, `good first issue`
- [ ] Create issue templates in `.github/ISSUE_TEMPLATE/`
- [ ] Create pull request template in `.github/pull_request_template.md`

---

## 🌐 XET Download Protocol Support (HIGH PRIORITY)

### Implementation Requirements
- [ ] Research XET download protocol specifications (NOT XetHub - distinct from legacy XetHub implementation)
- [ ] Determine if XET is compatible with HuggingFace Hub downloads
- [ ] Create `downloaders/xet_downloader.py` module for XET protocol support
- [ ] Add XET URL validation to `DownloadBackend.addDownload()`
- [ ] Update Add Download Dialog in `qml/main.qml` with XET examples
- [ ] Add XET integration tests in `tests/test_integration_xet.py`
- [ ] Document XET protocol usage in README.md
- [ ] Update AGENT_INSTRUCTIONS.md with XET architecture details

**IMPORTANT:** XET protocol ≠ XetHub (XetHub support was removed and will NEVER be re-implemented)

---

## 📝 Documentation Improvements (LOW PRIORITY)

### README.md Markdown Linting
- [ ] Fix MD022 warnings (blank lines around headings)
- [ ] Fix MD032 warnings (blank lines around lists)
- [ ] Fix MD036 warnings (emphasis as heading)
- [ ] Fix MD034 warnings (bare URLs - wrap in `<>`)
- [ ] Fix MD029 warnings (ordered list numbering)
Run: `markdownlint README.md --fix`

### tests/README.md Markdown Linting
- [ ] Fix heading formatting (MD022)
- [ ] Fix list formatting (MD032)
- [ ] Fix code fence formatting (MD031, MD040)
- [ ] Fix heading punctuation (MD026)
Run: `markdownlint tests/README.md --fix`

### Additional Documentation
- [ ] Create CONTRIBUTING.md with contribution guidelines
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Create CHANGELOG.md for version tracking
- [ ] Add screenshots to README.md
- [ ] Create animated GIF demo of the application

---

## 🚀 Feature Enhancements (FUTURE)

### Download Management
- [ ] Add resume support for interrupted downloads
- [ ] Add bandwidth throttling option
- [ ] Add scheduling (download at specific times)
- [ ] Add download queue prioritization (drag-and-drop reorder)
- [ ] Add parallel download support (multiple simultaneous downloads)

### UI/UX Improvements
- [ ] Add dark/light theme toggle
- [ ] Add custom accent color picker
- [ ] Add compact view mode
- [ ] Add download history view
- [ ] Add download statistics (total downloaded, average speed, etc.)
- [ ] Add system tray integration (minimize to tray)
- [ ] Add desktop notifications for completed downloads

### Platform Support
- [ ] Add support for Git LFS repositories
- [ ] Add support for Kaggle datasets
- [ ] Add support for direct URL downloads (generic HTTP/HTTPS)
- [ ] Add torrent support (optional)

### Advanced Features
- [ ] Add download verification (checksums, hashes)
- [ ] Add automatic retry on failure
- [ ] Add bandwidth monitoring graphs
- [ ] Add download filters (by file type, size, etc.)
- [ ] Add search within downloaded files
- [ ] Add cloud sync (save queue across devices)

---

## 🧪 Testing Improvements (MEDIUM PRIORITY)

### Test Coverage
- [ ] Increase `download_worker.py` coverage (currently 34%)
- [ ] Add tests for error handling in download worker
- [ ] Add tests for pause/resume functionality
- [ ] Add tests for cancellation scenarios
- [ ] Mock network failures and test recovery

### Integration Testing
- [ ] Add more integration tests with different file sizes
- [ ] Test with slow network conditions
- [ ] Test with network interruptions
- [ ] Test concurrent downloads
- [ ] Add performance benchmarks

### UI Testing
- [ ] Add QML UI tests
- [ ] Test view switching (List ↔ Grid)
- [ ] Test dialog validation
- [ ] Test touch interactions
- [ ] Test keyboard navigation

---

## 🔐 Security Enhancements (MEDIUM PRIORITY)

### Input Validation
- [ ] Add URL validation for malicious patterns
- [ ] Sanitize file paths before saving
- [ ] Add file size limits (prevent disk space exhaustion)
- [ ] Validate downloaded file types match expected

### Authentication
- [ ] Add secure token storage (system keychain integration)
- [ ] Add token refresh mechanism for HuggingFace
- [ ] Add support for SSH keys
- [ ] Encrypt saved downloads.json (optional)

### Audit
- [ ] Run security scan: `pip install safety && safety check`
- [ ] Check for known vulnerabilities in dependencies
- [ ] Add pre-commit hooks for secret detection
- [ ] Document security best practices in SECURITY.md

---

## 📦 Distribution (FUTURE)

### Package Managers
- [ ] Publish to PyPI: `pip install huggxet-downloader`
- [ ] Create Homebrew formula (macOS): `brew install huggxet-downloader`
- [ ] Create Chocolatey package (Windows): `choco install huggxet-downloader`
- [ ] Create Snap package (Linux): `snap install huggxet-downloader`
- [ ] Create Flatpak (Linux): `flatpak install huggxet-downloader`

### App Stores
- [ ] Submit to Microsoft Store (Windows)
- [ ] Submit to Mac App Store (macOS)
- [ ] Submit to Google Play Store (Android)
- [ ] Submit to Apple App Store (iOS)

### Auto-Updates
- [ ] Implement auto-update mechanism
- [ ] Add version check on startup
- [ ] Create update notification system
- [ ] Add changelog display on update

---

## 🎨 Branding (OPTIONAL)

### Visual Identity
- [ ] Design professional logo
- [ ] Create brand guidelines
- [ ] Design marketing materials
- [ ] Create website/landing page

### Social Media
- [ ] Create project website
- [ ] Set up Twitter/X account
- [ ] Create demo video for YouTube
- [ ] Write blog post announcing release

---

## ✅ Completed Items

- [x] Create virtual environment
- [x] Install all dependencies
- [x] Implement HuggingFace downloader
- [x] Create QML Material Design UI
- [x] Add download persistence (auto-save/load)
- [x] Write comprehensive unit tests (39 tests)
- [x] Write integration tests (18 tests)
- [x] Achieve 79% code coverage
- [x] Configure VS Code tasks (17 tasks)
- [x] Create PyInstaller build configuration
- [x] Add Windows/Linux/macOS build tasks
- [x] Create buildozer.spec for Android builds
- [x] Create pyproject.toml for iOS builds
- [x] Add mobile build tasks to VS Code
- [x] Update .gitignore for build artifacts
- [x] Write comprehensive documentation (README, SETUP, AGENT_INSTRUCTIONS, TASKS_GUIDE)
- [x] Add security requirements documentation
- [x] Enhance Add Download dialog with validation

---

## Priority Summary

**🔴 HIGH PRIORITY:**
1. Set up private submodule for agent instructions

**🟡 MEDIUM PRIORITY:**
2. Test mobile builds (if needed)
3. Improve test coverage (download_worker.py)
4. Add security enhancements

**🟢 LOW PRIORITY:**
5. Fix Markdown linting warnings
6. Add GitHub integrations
7. Feature enhancements
8. Distribution planning

---

**Last Updated:** November 20, 2025
