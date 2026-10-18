# VHS tape for the README demo GIF: https://github.com/charmbracelet/vhs
# Regenerate from the repository root with:  vhs docs/assets/demo.tape
# Needs vhs (with ttyd, ffmpeg and Chromium), Task, uv, a running Docker
# daemon, and compose/.env (a copy of compose/.env.example). The session
# starts and stops the default stack and uses host ports 8080 to 9000 and
# 18080.

Output docs/assets/demo.gif

Set Shell bash
Set FontSize 15
Set Width 1100
Set Height 620
Set Padding 16
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set Framerate 20
Set WaitPattern /^\$ ?$/
Set WaitTimeout 180s

# A plain prompt (so Wait knows when a command is done) and dockerctl from
# the locked project environment.
Hide
Type "export PS1='$ ' && alias dockerctl='uv run --quiet --locked --project cli dockerctl' && clear"
Enter
Show

# Admin passwords are generated, then compose waits for every healthcheck.
Type "task up"
Enter
Wait
Sleep 2s

Type "docker compose -f compose/docker-compose.yml ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'"
Enter
Wait
Sleep 3s

# A one-off container through the CLI: hardened by default, loopback only.
Type "dockerctl containers deploy nginxinc/nginx-unprivileged:1.30.6-alpine3.24 -n web -p 18080:8080"
Enter
Wait
Sleep 1s

Type "docker inspect web --format 'read-only={{.HostConfig.ReadonlyRootfs}} cap-drop={{.HostConfig.CapDrop}} pids={{.HostConfig.PidsLimit}}'"
Enter
Wait
Sleep 3s

Type "curl -s -o /dev/null -w 'web -> %{http_code}\n' http://127.0.0.1:18080/"
Enter
Wait
Sleep 2s

Type "dockerctl containers rm --force web"
Enter
Wait
Sleep 1s

Type "task down"
Enter
Wait
Sleep 2s
