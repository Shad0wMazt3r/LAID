# Local AI-assisted Development
Local AI-assisted Development (or LAID for short) is a series of experiments to use Local Large Language Models (L-LLMs) to do AI assisted software development. I plan on using the following workflow:

1. **LM Studio**: LM Studio will host the model and provide OpenAI like endpoints to access the model
2. **LAID Script/Extension**: This script, currently named `laid.py`, is designed to interact with the L-LLM through LM Studio. It handles prompt generation, provides context to the LLM, manages file operations (reading, writing, deleting), and integrates with VS Code for seamless development.
3. **Visual Studio Code**: I will use this to monitor what my code looks like, make any modifications if I need to.
4. **Git**: This will save changes and help to diff.

**File Details:**
*   `laid.json`: Project configuration file.
*   `main.py`: Main Python script.
*   `requirements.txt`: Lists project dependencies.
*   `.git`: Git repository directory.
*   `config`, `core`, `models`, `tools`, `ui`: Directories containing various project components.

**Running the Project:**

1.  Clone the repository: `git clone [repository URL]` (Replace [repository URL] with the actual URL)
2. Navigate to the project directory: `cd LAID`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the main script: `python laid.py`

### Features
- Local LLM integration via LM Studio
- File operations (read, write, edit)
- Command execution
- Web browsing and search
- CVE vulnerability search
- Agent modes (planning, acting, logging)
- Real-time pause/resume with Ctrl+C