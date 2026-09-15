# OKP v0.2 to LeRobot v3 annotation mapping

This is a normative mapping of OKP meaning to metadata attached to an existing
LeRobot v3 recording. It is not a converter and does not make an OKP Event a
trainable robot-learning episode.

| OKP v0.2 | LeRobot v3 destination | Rule |
| --- | --- | --- |
| Event time interval (`t_start`, `t_end`) | episode/frame interval selected through episode metadata | Convert timestamps only when the recording clock and OKP clock have a documented alignment. |
| `verb` | natural-language task description in `meta/tasks.jsonl` | Use the canonical OKP verb as the leading task token. |
| `variant`, `object_refs` | task-description qualifiers | Append only non-personal, rights-cleared labels; preserve the original OKP fields in sidecar provenance. |
| `event_id`, `okp_version` | sidecar annotation provenance | Preserve verbatim so an annotation can be traced to the source Event and protocol release. |
| `outcome`, `quality_flags`, `measures` | sidecar episode annotations | Do not coerce these into action, state or reward tensors without a separately specified transformation. |
| Station/Equipment context | sidecar embodiment context | Resolve references outside the Event and record the source revision. |

LeRobot v3 stores frame-level low-dimensional state/action/timestamps in
Parquet, video in MP4 and schema/task/episode metadata under `meta/`. OKP v0.2
contains operational intervals and labels, not camera frames, states, actions,
motor trajectories, calibration or clock alignment. A runnable converter is
therefore deferred until a rights-cleared paired OKP + LeRobot fixture exists;
shipping an untestable stub would overstate interoperability.

T0/T1 material is not made shareable by conversion. Apply the OKP tier policy
before export and the LeRobot dataset owner's rights and privacy controls after it.
