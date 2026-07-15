# Independent AWS realtime infrastructure

Phase 7 owns the Terraform root in this directory. It must have independent
state and must not reference local Compose endpoints, volumes, credentials, or
runtime services.
