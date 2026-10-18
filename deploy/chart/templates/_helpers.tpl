{{/*
Chart name, truncated to the 63 characters a DNS label allows.
*/}}
{{- define "devops-stack.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Release-scoped name. A release named after the chart is not repeated.
*/}}
{{- define "devops-stack.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Name of one component's objects: <fullname>-<component>.
Called with (dict "root" $ "component" "nginx").
*/}}
{{- define "devops-stack.componentName" -}}
{{- printf "%s-%s" (include "devops-stack.fullname" .root | trunc 52 | trimSuffix "-") .component }}
{{- end }}

{{- define "devops-stack.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Labels that select the release's pods. Every NetworkPolicy keys on these.
*/}}
{{- define "devops-stack.selectorLabels" -}}
app.kubernetes.io/name: {{ include "devops-stack.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "devops-stack.labels" -}}
helm.sh/chart: {{ include "devops-stack.chart" . }}
{{ include "devops-stack.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector and labels for one component, called with (dict "root" $ "component" "nginx").
*/}}
{{- define "devops-stack.componentSelectorLabels" -}}
{{ include "devops-stack.selectorLabels" .root }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "devops-stack.componentLabels" -}}
{{ include "devops-stack.labels" .root }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "devops-stack.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "devops-stack.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Image reference: repository:tag, plus @digest when one is set. An empty tag
falls back to the chart's appVersion. Called with (dict "root" $ "image" .Values.nginx.image).
*/}}
{{- define "devops-stack.image" -}}
{{- $tag := .image.tag | default .root.Chart.AppVersion -}}
{{- if .image.digest -}}
{{- printf "%s:%s@%s" .image.repository $tag .image.digest -}}
{{- else -}}
{{- printf "%s:%s" .image.repository $tag -}}
{{- end -}}
{{- end }}

{{/*
Pod-level security context shared by every pod: non-root with the image's
fixed IDs and the RuntimeDefault seccomp profile. Called with the component's
values (runAsUser, runAsGroup).
*/}}
{{- define "devops-stack.podSecurityContext" -}}
runAsNonRoot: true
runAsUser: {{ .runAsUser }}
runAsGroup: {{ .runAsGroup }}
seccompProfile:
  type: RuntimeDefault
{{- end }}

{{/*
Container-level security context shared by every container.
*/}}
{{- define "devops-stack.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
privileged: false
capabilities:
  drop: ["ALL"]
{{- end }}

{{/*
The only writable path in every container, held in memory like the compose
tmpfs mounts.
*/}}
{{- define "devops-stack.tmpVolume" -}}
- name: tmp
  emptyDir:
    medium: Memory
    sizeLimit: 16Mi
{{- end }}
