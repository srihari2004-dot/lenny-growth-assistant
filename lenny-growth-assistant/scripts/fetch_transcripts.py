from pathlib import Path
import subprocess

TARGET = Path("data/lenny-source")
URL = "https://github.com/LennysNewsletter/lennys-newsletterpodcastdata.git"

TARGET.parent.mkdir(parents=True, exist_ok=True)
if TARGET.exists() and (TARGET / ".git").exists():
    subprocess.run(["git", "-C", str(TARGET), "pull", "--ff-only"], check=True)
else:
    subprocess.run(["git", "clone", "--depth", "1", URL, str(TARGET)], check=True)
print(f"Dataset ready at {TARGET}")
