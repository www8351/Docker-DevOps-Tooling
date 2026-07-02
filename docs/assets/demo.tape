# VHS tape for the README demo GIF — https://github.com/charmbracelet/vhs
# Regenerate with:  vhs docs/assets/demo.tape
# Requires: vhs, a running Docker daemon, and compose/.env (copy of .env.example).

Output docs/assets/demo.gif

Set FontSize 16
Set Width 1200
Set Height 640
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "task up"
Enter
Sleep 12s

Type "docker compose -f compose/docker-compose.yml ps"
Enter
Sleep 4s

Type "dockerctl containers ls --json"
Enter
Sleep 3s

Type "dockerctl --version"
Enter
Sleep 2s

Type "task down"
Enter
Sleep 6s
