# LinkedIn + CV assets (use verbatim — same pitch line everywhere)

## One-line pitch (CV Projects section, LinkedIn Featured, anywhere)

> Rebuilt a legacy Docker lab into a hardened, released toolkit — typed Python CLI
> (mypy strict, 45 tests, 100% coverage), read-only cap-dropped containers (one image cut
> 78 MB → 7 MB), and CI that boots the full stack live before publishing multi-arch,
> cosign-signed images with SBOMs to GHCR.

CV: spell out the URL — github.com/www8351/Docker-DevOps-Tooling

## LinkedIn headline keywords (align with repo topics)

DevOps Engineer | Docker · Kubernetes (EKS) · AWS · Container Security · CI/CD Supply
Chain · Terraform · Python

## LinkedIn post

<!-- Weekday morning. Attach the demo GIF once recorded. Post the repo link as the FIRST
     COMMENT immediately after publishing (outbound links in the body suppress reach).
     Reply to every comment same day. The socket-bug story deliberately lives in the
     r/devops post and the article — this post uses the image-diet hook so the same
     audience doesn't read the same anecdote twice. -->

---

I deleted 71 MB of attack surface from one Docker image. Here's what was hiding in it.

The container ran a trivial counter script. The image shipped openssh-server, sshpass,
and tcpdump — none of it used, all of it exactly what a security scanner flags first.
Nobody chose that; it accumulated because an Ubuntu base and a few apt-get lines are the
path of least resistance.

The rebuild: multi-stage Dockerfile, shellcheck gate in stage one (broken shell fails the
build), and an alpine runtime stage that carries only the validated script — owned by a
fixed-ID non-root user, read-and-execute only. 78 MB became 7 MB, and the Trivy
HIGH/CRITICAL gate passes clean.

The lesson that stuck: the fastest way to pass an image scan isn't patching findings,
it's having almost nothing to scan.

Full write-up (with the CI bug the pipeline caught along the way) — link in the first
comment.

#DevOps #Docker #ContainerSecurity #CICD

---

## r/devops post

<!-- Lead with the lesson. NO repo link in the post — share it only if someone asks in
     comments. Title's "for weeks" and the article's "hiding for weeks" deliberately
     match. -->

**Title:** Making CI actually boot the stack caught a bug that "works on my machine" hid for weeks

**Body:**

My compose stack is locked down about as far as compose allows — read-only rootfs,
cap_drop ALL, non-root everywhere. CI validated the config on every push and stayed
green for weeks.

Then I added a job that *boots* the stack (`docker compose up -d --wait` so healthchecks
gate the merge) plus a live test of the CLI image against the runner's socket. First run:
permission denied. The CLI runs as UID 10001; on my machine, Docker Desktop's socket was
wide open, but the GitHub runner's is root:docker. Fixed without giving up non-root:

```
--group-add "$(stat -c '%g' /var/run/docker.sock)"
```

(Yes, socket access is root-equivalent — it's a Docker-management CLI, that's the one
privilege it exists to have. The point is it gets that and nothing else.)

Lesson: config validation isn't verification. If the pipeline doesn't run the thing, the
pipeline doesn't know.

What's the highest-value live check your CI runs beyond the unit suite? Curious what's
actually caught real bugs for other people.
