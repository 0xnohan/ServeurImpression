# CLAUDE.md - Serveur Impression

Python print server that runs **on the client's machine**, not on a web server.
It polls the application server for queued documents, downloads each one, sends
it to the configured printer, then deletes it locally and remotely. It also
drives the TPE (card payment terminal) section.

**Not a PHP project.** Nothing in the architecture, encoding or deployment
sections of `../CLAUDE.md` applies here.

## (!) This project is duplicated

`../pos-server/` is the **same codebase** - `app.py` is byte-identical between
the two, and `Core/` holds the same three modules. The two directories have
diverged only in what surrounds the code:

| | `ServeurImpression` | `pos-server` |
| --- | --- | --- |
| `DockerFile` | yes | no |
| `executables_impression.zip` | yes | no |
| `Setup_BTP-R880NP V1.12A.zip` (printer driver) | yes | no |
| `venv/` committed | no | yes |
| Last commit | 2025-08-14 | 2025-08-14 |

Decide which one is canonical before doing any work. A change made in one is
invisible to the other, and there is no mechanism keeping them in sync.

## Structure

- `app.py` - entry point / user interface
- `Core/serveur.py` - the main loop over printer sections and the TPE
- `Core/fonctions.py` - `logMessage`, `getIP`, `chargerConfig`,
  `telechargerFichier`, `imprimerFichier`, `supprimerFichier`
- `Core/fonctionsIMPR.py` - printer-specific handling
- `data/` - runtime data
- `config.json` - user settings, written by the UI
- `log.txt` - written by `logMessage` at every branch point; read it first when
  something misbehaves in the field

Printing is OS-dependent (`imprimerFichier` branches per platform), and the
target printer is a Brother BTP-R880NP - its driver is bundled here.

## Notable

- Documentation (`Readme.md`) is in French.
- No deploy hook: this is not rsynced anywhere. It is packaged and installed on
  the client's machine, which is what `executables_impression.zip` and the
  `DockerFile` are for.
- Dormant since 2025-08-14.
