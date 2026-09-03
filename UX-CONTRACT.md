# Tidyra UX Contract

## Empty-directory cleanup

Source: [ADR-0011](docs/docs/adrs/0011-explicit-empty-directory-cleanup.md).

| Stage | Behavior |
|---|---|
| Home | **Remove empty folders after organizing** is unchecked by default. |
| Preview | When selected, list every folder that will be checked and state that only folders still empty will be removed. |
| Confirm | The final action reads **Organize Files and Remove Empty Folders**. |
| Execute | Move planned files, then attempt non-recursive removal deepest-first. Reject symlinks and junctions. |
| Result | Report the folders actually removed. Leave directories containing anything untouched. |

The operation is a hard directory removal only when the operating system
confirms the directory is empty. Tidyra never deletes files or recursively
deletes a directory.

## Date-folder refresh

Source: [ADR-0013](docs/docs/adrs/0013-date-folder-modified-times.md).

The preview lists date folders whose **Date modified** values will be refreshed
from their routed files. If no files need moving, the final action reads
**Refresh Date Folder Times**. Tidyra does not change **Date created**.
