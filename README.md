## Kekkoutant Telegram Bot

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The project requires Python 3.8 and above. You can check your Python version with the following command:

```bash
python --version
```

The project also requires several Python packages. You can install them with the following command:

```bash
pip install -r requirements.txt
```

### Installation

First, clone the repository to your local machine:

```bash
git clone https://github.com/adz1doubled/kekkoutant
```

Next, navigate to the project folder:

```bash
cd kekkoutant
```

Then, set up a Python virtual environment to manage your project's dependencies. First, create the virtual environment:

```bash
python -m venv myenv
```

Next, activate the virtual environment:

- For bash/zsh:

```bash
source myenv/bin/activate
```

- For fish:

```fish
source myenv/bin/activate.fish
```

- For Windows (PowerShell):
```powershell
myenv\Scripts\Activate
```

- For Windows (Command Prompt - cmd):
```cmd
myenv\Scripts\activate.bat
```

After activating the virtual environment, install the project's dependencies:

```bash
pip install -r requirements.txt
```

### Setting Up Environment Variables

Copy `.env.example` to `.env`

```bash
cp .env.example .env
```

Fill in the required values in `.env`

### Running the Project

With the virtual environment activated and all dependencies installed, you can now run your project with:

```bash
python app/main.py
```