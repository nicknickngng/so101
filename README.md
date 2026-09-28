# so101

LeRobot environment for the SO101 arm, managed with uv.

## Setup (Windows)

```powershell
winget install astral-sh.uv
winget install Gyan.FFmpeg.Shared --version 8.1.2   # TorchCodec supports ffmpeg 4-8, not 9
winget pin add Gyan.FFmpeg.Shared
# restart the terminal (fully restart VS Code if using its terminal) so PATH updates

git clone <this-repo>
cd so101
uv sync
```

Check it:

```powershell
uv run python -c "import torch, torchcodec.decoders; print(torch.cuda.is_available())"
```

## Usage

Run LeRobot commands through uv, e.g. `uv run lerobot-find-port`.
Never use plain `pip` — it installs into system Python. Use `uv add <pkg>` to add dependencies.
