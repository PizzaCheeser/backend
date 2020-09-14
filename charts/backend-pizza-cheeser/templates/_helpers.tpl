{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "backend-pizza-cheeser.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "backend-pizza-cheeser.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "backend-pizza-cheeser.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "backend-pizza-cheeser.labels" -}}
helm.sh/chart: {{ include "backend-pizza-cheeser.chart" . }}
{{ include "backend-pizza-cheeser.selectorLabels" . }}
environment: {{ .Values.sentry.environment | quote }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Common env variables
*/}}
{{- define "backend-pizza-cheeser.env_vars" -}}
- name: SENTRY_DSN
  value: {{ .Values.sentry.dsn | quote }}
- name: SENTRY_ENVIRONMENT
  value: {{ .Values.sentry.environment | quote }}
- name: SENTRY_RELEASE
  value: {{ .Values.image.tag | quote }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "backend-pizza-cheeser.selectorLabels" -}}
app.kubernetes.io/name: {{ include "backend-pizza-cheeser.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "backend-pizza-cheeser.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "backend-pizza-cheeser.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
