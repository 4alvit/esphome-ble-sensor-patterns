# CI and source release workflow

The `Quality gate` workflow retains the existing validation workflows and all
eight ESPHome compile matrix entries. It requires the new native parser and
source contracts plus the shared workflow/release contracts. Parser regression
tests run under ASan and UBSan without devices, radio or MQTT.

`release-pipeline.yml` is the source candidate entry point. Default-branch pushes
may publish beta after checks and extracted-source acceptance. Explicit RC
requests additionally run the Linux libFuzzer mutation campaign. Every asset and
receipt is bound to its exact source and frozen version plan. Stable remains
separate and is not part of this implementation's delivery validation.

See [source releases](source-releases.md), the [Inkbird contract](inkbird-contract.md)
and the [generated runbook](../RELEASING.md). The released product is an explicit
source archive, not a prebuilt firmware image or hardware-certification result.
