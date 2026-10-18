{{/*
Deployment and Service for one web server (nginx or httpd). Both listen on
8080 as their image's own non-root user and serve read-only content; the
only writable path is /tmp. Called with
(dict "root" $ "component" "httpd" "values" .Values.httpd "config" "<httpd.conf>"),
where config is optional and, when set, is mounted over the image's
/usr/local/apache2/conf/httpd.conf from the component's ConfigMap.
*/}}
{{- define "devops-stack.web" -}}
{{- $name := include "devops-stack.componentName" . -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ $name }}
  labels:
    {{- include "devops-stack.componentLabels" . | nindent 4 }}
spec:
  replicas: {{ .values.replicas }}
  selector:
    matchLabels:
      {{- include "devops-stack.componentSelectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "devops-stack.componentLabels" . | nindent 8 }}
      {{- with .config }}
      annotations:
        # Roll the pods when the mounted configuration changes.
        checksum/config: {{ . | sha256sum }}
      {{- end }}
    spec:
      serviceAccountName: {{ include "devops-stack.serviceAccountName" .root }}
      automountServiceAccountToken: false
      enableServiceLinks: false
      securityContext:
        {{- include "devops-stack.podSecurityContext" .values | nindent 8 }}
      containers:
        - name: {{ .component }}
          image: {{ include "devops-stack.image" (dict "root" .root "image" .values.image) | quote }}
          imagePullPolicy: {{ .values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          readinessProbe:
            httpGet:
              path: /
              port: http
            periodSeconds: 10
            timeoutSeconds: 5
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          resources:
            {{- toYaml .values.resources | nindent 12 }}
          securityContext:
            {{- include "devops-stack.containerSecurityContext" . | nindent 12 }}
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            {{- if .config }}
            - name: config
              mountPath: /usr/local/apache2/conf/httpd.conf
              subPath: httpd.conf
              readOnly: true
            {{- end }}
      volumes:
        {{- include "devops-stack.tmpVolume" . | nindent 8 }}
        {{- if .config }}
        - name: config
          configMap:
            name: {{ $name }}
        {{- end }}
---
apiVersion: v1
kind: Service
metadata:
  name: {{ $name }}
  labels:
    {{- include "devops-stack.componentLabels" . | nindent 4 }}
spec:
  type: {{ .values.service.type }}
  selector:
    {{- include "devops-stack.componentSelectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .values.service.port }}
      targetPort: http
      protocol: TCP
{{- end }}
