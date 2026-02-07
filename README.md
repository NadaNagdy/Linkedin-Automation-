# LinkedIn Automation 🚀

A Python-based automation tool to scrape trending health/tech news and post them to LinkedIn.

## Features
- **Scraper**: Fetches trending articles from TechCrunch and PubMed.
- **Poster**: Automates posting content to your LinkedIn profile.
- **OAuth Helper**: Built-in script to generate LinkedIn Access Tokens.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NadaNagdy/Linkedin-Automation-.git
   cd Linkedin-Automation-
   ```

2. **Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configuration**:
   Create a `.env` file in the root directory with the following credentials:
   ```env
   LINKEDIN_TOKEN=your_access_token_here
   LINKEDIN_PERSON_URN=your_person_urn_here
   ```
   *Note: The project uses `python-dotenv` to automatically load these variables.*

   > **Note**: You can find your credentials using the helper scripts below.

## Tools

### 1. Generate Access Token (`scripts/generate_token.py`)
If you don't have a valid token or it has expired:
```bash
python3 scripts/generate_token.py
```
- You will be asked for your **Client Secret**.
- Follow the browser prompt to authorize.
- Copy the generated `Access Token` to your `.env` file.

### 2. Verify Connection (`main_script.py`)
Checks if your token is valid and fetches your User URN.
```bash
python3 main_script.py
```
- Copy the `URN` (e.g., `dItyz0f_43`) to your `.env` file as `LINKEDIN_PERSON_URN`.

### 3. Run Scraper (`scripts/scraper.py`)
Fetches latest trends (can be imported or run directly if modified).

### 4. Post to LinkedIn (`scripts/linkedin_poster.py`)
Uses the configured token and URN to post content.
- Supports posting to personal profiles (default).
- Supports posting to Company Pages by providing the `author_urn` (e.g., `urn:li:organization:123456`).

### 5. Run Full Automation (`run_bot.py`)
The main script that orchestrates the entire flow:
1.  Fetches trends using `scraper.py`.
2.  Formats a post.
3.  Posts to LinkedIn using `linkedin_poster.py`.

```bash
python3 run_bot.py
```
*To post to a Company Page automatically, set `LINKEDIN_AUTHOR_URN` in your environment or GitHub Secrets.*
