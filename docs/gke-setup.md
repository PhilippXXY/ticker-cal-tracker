# GKE Cluster Setup for `ticker-cal-tracker`

This document describes the initial Kubernetes (GKE) setup for the backend.  
It is **documentation only** – no application deployment manifests are committed yet.

---

## 1. Project and cluster

- **GCP project**: `ticker-cal-tracker`
- **GKE mode**: Autopilot
- **Cluster name**: `ticker-cal-tracker-cluster`
- **Region**: `europe-west2` (London)
- **Network**: default VPC
- **Purpose**: groundwork for a future production/staging deployment of the API

At this stage, the cluster only runs a demo workload (nginx) to confirm that:

- the control plane is reachable
- nodes can be provisioned
- a public LoadBalancer service exposes traffic correctly

---

## 2. How to connect to the cluster

From **Cloud Shell** (or any machine with `gcloud` and `kubectl` configured):

```bash
gcloud container clusters get-credentials ticker-cal-tracker-cluster \
  --region europe-west2 \
  --project ticker-cal-tracker
```
