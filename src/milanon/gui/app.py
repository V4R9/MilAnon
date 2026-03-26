"""MilAnon Streamlit GUI — local browser interface for anonymization."""

from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

import streamlit as st

from milanon import __version__

# Path to bundled reference data
_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# Path to user config
_CONFIG_PATH = Path.home() / ".milanon" / "config.json"


def _clean_path(raw: str) -> str:
    """Strip surrounding whitespace and single/double quotes from a path input."""
    return raw.strip().strip("'\"")


def _load_config() -> dict:
    """Load project config from ~/.milanon/config.json."""
    if _CONFIG_PATH.exists():
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def _save_config(data: dict) -> None:
    """Save project config to ~/.milanon/config.json."""
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _get_config_value(key: str, default: str = "") -> str:
    """Get a single config value by key."""
    return _load_config().get(key, default)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MilAnon",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

def _make_repo():
    from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
    from milanon.config.settings import ensure_db_dir

    db_path = ensure_db_dir()
    return SqliteMappingRepository(db_path)


def _load_municipalities() -> list[str]:
    csv_path = _DATA_DIR / "swiss_municipalities.csv"
    if not csv_path.exists():
        return []
    names: set[str] = set()
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("name", "").strip()
            if name and len(name) >= 3:
                names.add(name)
    return sorted(names)


def _make_anonymize_uc(repo):
    from milanon.adapters.recognizers.list_recognizer import ListRecognizer
    from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
    from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
    from milanon.domain.anonymizer import Anonymizer
    from milanon.domain.mapping_service import MappingService
    from milanon.domain.recognition import RecognitionPipeline
    from milanon.usecases.anonymize import AnonymizeUseCase

    service = MappingService(repo)
    municipality_names = _load_municipalities()
    pipeline = RecognitionPipeline(
        [PatternRecognizer(), MilitaryRecognizer(), ListRecognizer(repo, municipality_names)]
    )
    anonymizer = Anonymizer(service)
    return AnonymizeUseCase(pipeline, anonymizer, repo)


def _make_deanonymize_uc(repo):
    from milanon.domain.deanonymizer import DeAnonymizer
    from milanon.domain.mapping_service import MappingService
    from milanon.usecases.deanonymize import DeAnonymizeUseCase

    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    return DeAnonymizeUseCase(deanonymizer, repo)


def _init_reference_data(repo):
    """Initialize reference data (municipalities + military units) and return result."""
    from milanon.usecases.init_reference_data import InitReferenceDataUseCase
    return InitReferenceDataUseCase(repo, _DATA_DIR).execute()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🔒 MilAnon")
st.sidebar.markdown("Swiss Military Document Anonymizer")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🎯 LLM Workflow",
        "🔒 Anonymize",
        "🔓 De-Anonymize",
        "📄 DOCX Export",
        "📚 Doctrine",
        "🚀 Project Generator",
        "📥 DB Import",
        "📊 DB Stats",
        "⚙️ Config",
    ],
    index=0,
)

st.sidebar.divider()
st.sidebar.caption("All processing is local. No data leaves your machine.")
st.sidebar.caption(f"Version {__version__}")


# ===========================================================================
# 🎯 LLM Workflow page
# ===========================================================================

if page == "🎯 LLM Workflow":
    st.title("🎯 LLM Workflow")
    st.markdown(
        "Assemble doctrine-aware prompts for the 5+2 Aktionsplanungsprozess, "
        "or use free-form templates."
    )

    tab_workflow, tab_free, tab_unpack = st.tabs(
        ["5+2 Workflow", "Freier Modus", "Unpack Response"]
    )

    # -------------------------------------------------------------------
    # Tab 1 — 5+2 Workflow Mode
    # -------------------------------------------------------------------
    with tab_workflow:
        col1, col2 = st.columns(2)
        with col1:
            wf_mode = st.radio(
                "Modus",
                ["berrm", "adf"],
                index=0 if _get_config_value("mode", "berrm") == "berrm" else 1,
                horizontal=True,
                key="wf_mode",
            )
        with col2:
            wf_unit = st.text_input(
                "Einheit",
                value=_get_config_value("unit", ""),
                placeholder='z.B. "Inf Kp 56/1"',
                key="wf_unit",
            )

        wf_workflow = st.selectbox(
            "Workflow",
            [
                "analyse — Problemerfassung (5+2 Schritt 1)",
                "bdl — Beurteilung der Lage (5+2 Schritt 2)",
                "entschluss — Entschlussfassung (5+2 Schritt 3)",
                "ei-bf — Einsatzbefehl (5+2 Schritt 5)",
                "wachtdienst — Wachtdienstbefehl",
                "dossier-check — Dossier-Qualitätsprüfung (Schritt 0)",
            ],
            key="wf_workflow",
        )
        workflow_name = wf_workflow.split(" — ")[0].strip()

        wf_step = st.number_input(
            "5+2 Schritt (optional)",
            min_value=0,
            max_value=5,
            value=0,
            help="0 = auto (determined by workflow). 1-5 = specific step.",
            key="wf_step",
        )

        wf_input = st.text_input(
            "Anonymisierte Dokumente",
            value="",
            placeholder="/path/to/anonymized/output",
            key="wf_input",
        )

        wf_context = st.text_input(
            "Kontext (vorherige Schritte)",
            value="",
            placeholder="Pfad zu Vault/Planung/ (optional)",
            help="Include Vault files from previous 5+2 steps for step chaining.",
            key="wf_context",
        )

        wf_output = st.text_input(
            "Pack speichern unter (optional)",
            value="",
            placeholder="/path/to/pack.md",
            key="wf_output",
        )

        if st.button(
            "📋 Prompt generieren", type="primary", key="btn_wf_pack", disabled=not wf_input
        ):
            try:
                from milanon.usecases.generate_context import GenerateContextUseCase
                from milanon.usecases.workflow_pack import WorkflowPackUseCase

                repo = _make_repo()
                ctx_gen = GenerateContextUseCase(repo)
                wf_uc = WorkflowPackUseCase(repo, ctx_gen)

                pack_text, pack_result = wf_uc.execute(
                    workflow=workflow_name,
                    mode=wf_mode,
                    step=wf_step if wf_step > 0 else None,
                    input_path=Path(_clean_path(wf_input)),
                    unit=wf_unit.strip(),
                    context_path=Path(_clean_path(wf_context)) if wf_context.strip() else None,
                    output_path=Path(_clean_path(wf_output)) if wf_output.strip() else None,
                    copy_clipboard=True,
                )

                token_estimate = pack_result.total_chars // 4
                ctx_pct = token_estimate * 100 // 200_000

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Dokumente", pack_result.documents_included)
                col_b.metric("~Tokens", f"~{token_estimate:,}")
                col_c.metric("Context Window", f"{ctx_pct}%")

                if pack_result.copied_to_clipboard:
                    st.success("Prompt generiert und in Zwischenablage kopiert.")
                else:
                    st.warning("Prompt generiert. Konnte nicht in Zwischenablage kopieren.")

                if pack_result.output_path:
                    st.info(f"Gespeichert: `{pack_result.output_path}`")

                with st.expander("Prompt-Vorschau", expanded=False):
                    truncated = "\n\n[... truncated ...]" if len(pack_text) > 5000 else ""
                    st.code(pack_text[:5000] + truncated, language="markdown")

            except Exception as exc:
                st.error(f"Fehler: {exc}")

    # -------------------------------------------------------------------
    # Tab 2 — Free Mode (classic pack builder)
    # -------------------------------------------------------------------
    with tab_free:
        st.subheader("Generate LLM Context File")
        st.markdown(
            "Build a context file that tells the LLM about your unit hierarchy and "
            "placeholder rules. Paste it before your anonymized document when prompting Claude."
        )

        from milanon.usecases.generate_context import GenerateContextUseCase

        repo = _make_repo()
        ctx_uc = GenerateContextUseCase(repo)
        units = ctx_uc.get_available_units()

        if not units:
            st.info("No units found in database. Import personnel data first (DB Import page).")
        else:
            selected_unit = st.selectbox(
                "Your unit",
                options=units,
                format_func=lambda u: f"{u.original_value} ({u.level})",
            )

            ctx_output = st.text_input(
                "Save context file to",
                value="",
                placeholder="z.B. output/CONTEXT.md",
                help="Path where CONTEXT.md will be written.",
            )

            if st.button("Generate Context", type="primary"):
                try:
                    ctx_uc.generate(selected_unit.original_value, Path(_clean_path(ctx_output)))
                    content = Path(_clean_path(ctx_output)).read_text(encoding="utf-8")
                    st.success(f"Context file written to `{ctx_output}`")
                    st.markdown("**Preview — copy this before your anonymized document:**")
                    st.code(content, language="markdown")
                    st.download_button(
                        "Download CONTEXT.md",
                        data=content,
                        file_name="CONTEXT.md",
                        mime="text/markdown",
                    )
                except Exception as exc:
                    st.error(f"Error generating context: {exc}")

        st.divider()
        st.subheader("Pack Builder")
        st.markdown(
            "Assemble context + template + anonymized documents"
            " into a single clipboard-ready prompt."
        )

        from milanon.usecases.pack import PackUseCase
        from milanon.usecases.pack import list_templates as _list_templates

        pack_templates = _list_templates()
        template_options = [t["name"] for t in pack_templates] if pack_templates else ["frei"]

        pack_col1, pack_col2 = st.columns(2)
        with pack_col1:
            pack_input = st.text_input(
                "Anonymized documents folder",
                placeholder="/path/to/anon/output",
                key="pack_input",
                help="Folder with anonymized .md/.txt files.",
            )
        with pack_col2:
            pack_template = st.selectbox(
                "Template",
                options=template_options,
                key="pack_template",
            )

        pack_unit = st.text_input(
            "Your unit (optional)",
            placeholder='e.g. "Inf Kp 56/1"',
            key="pack_unit",
        )
        pack_prompt = st.text_area(
            "Custom prompt (optional, used with template 'frei')",
            height=80,
            key="pack_prompt",
        )
        pack_output = st.text_input(
            "Save pack to file (optional)",
            placeholder="/path/to/pack.md",
            key="pack_output",
        )

        if st.button(
            "Build Pack & Copy to Clipboard",
            type="primary", key="btn_pack", disabled=not pack_input,
        ):
            try:
                repo_pack = _make_repo()
                pack_uc = PackUseCase(repo_pack)
                _, pack_result = pack_uc.execute(
                    Path(_clean_path(pack_input)),
                    template_name=pack_template,
                    user_unit=pack_unit.strip(),
                    user_prompt=pack_prompt.strip(),
                    output_path=Path(_clean_path(pack_output)) if pack_output.strip() else None,
                    copy_clipboard=True,
                )
                msg = (
                    f"Pack built — {pack_result.documents_included} doc(s), "
                    f"{pack_result.total_chars} chars."
                )
                if pack_result.copied_to_clipboard:
                    st.success(msg + " Copied to clipboard.")
                else:
                    st.warning(msg + " Could not copy to clipboard (macOS/Linux only).")
                if pack_result.output_path:
                    st.info(f"Pack saved to `{pack_result.output_path}`")
            except Exception as exc:
                st.error(f"Error building pack: {exc}")

    # -------------------------------------------------------------------
    # Tab 3 — Unpack Response
    # -------------------------------------------------------------------
    with tab_unpack:
        st.subheader("De-Anonymize LLM Output")
        st.markdown(
            "Paste Claude's response here to restore real names, then save to your vault."
        )

        llm_output = st.text_area(
            "Paste Claude's output",
            height=300,
            placeholder="Paste the LLM response here…",
        )

        unpack_col1, unpack_col2 = st.columns(2)
        with unpack_col1:
            save_path = st.text_input(
                "Output folder",
                placeholder="/path/to/obsidian/vault/",
                help="Folder where de-anonymized file(s) will be written.",
            )
        with unpack_col2:
            split_sections = st.checkbox(
                "Split on --- separators (write separate files)",
                help="When enabled, splits on --- and writes one file per section.",
            )

        can_run = bool(llm_output.strip() and save_path.strip())
        if st.button("De-Anonymize & Save", type="primary", disabled=not can_run):
            try:
                from milanon.domain.deanonymizer import DeAnonymizer
                from milanon.domain.mapping_service import MappingService
                from milanon.usecases.unpack import UnpackUseCase

                repo_da = _make_repo()
                service = MappingService(repo_da)
                deanonymizer = DeAnonymizer(service)
                unpack_uc = UnpackUseCase(deanonymizer)

                unpack_result = unpack_uc.execute(
                    Path(_clean_path(save_path)),
                    input_text=llm_output,
                    split_sections=split_sections,
                )

                st.success(
                    f"Saved {unpack_result.files_written} file(s). "
                    f"Resolved {unpack_result.placeholders_resolved} placeholder(s)."
                )
                for f in unpack_result.output_files:
                    st.caption(f"→ `{f}`")
                if unpack_result.warnings:
                    n_warn = len(unpack_result.warnings)
                    with st.expander(f"⚠️ {n_warn} unresolved placeholder(s)"):
                        for w in unpack_result.warnings:
                            st.warning(w)
            except Exception as exc:
                st.error(f"Error: {exc}")


# ===========================================================================
# 🔒 Anonymize page
# ===========================================================================

elif page == "🔒 Anonymize":
    st.title("🔒 Anonymize Documents")
    st.markdown("Replace sensitive entities with placeholders before sending to an LLM.")

    col1, col2 = st.columns(2)
    with col1:
        input_path = st.text_input(
            "Input folder or file",
            placeholder="/path/to/input",
            help="Folder or single file to anonymize.",
        )
    with col2:
        output_path = st.text_input(
            "Output folder",
            placeholder="/path/to/output",
            help="Where anonymized files are written.",
        )

    col_level, col_opts = st.columns([1, 3])
    with col_level:
        anon_level = st.radio(
            "Anonymisierungsstufe",
            ["dsg", "full"],
            index=0 if _get_config_value("level", "dsg") == "dsg" else 1,
            horizontal=True,
            key="anon_level",
            help="DSG = nur Personendaten (DSGVO), Full = alle Entitäten inkl. Einheiten/Orte",
        )

    col3, col4, col5, col6, col7 = st.columns(5)
    with col3:
        recursive = st.checkbox("Recursive (include subfolders)")
    with col4:
        force = st.checkbox("Force (reprocess all files)")
    with col5:
        dry_run = st.checkbox("Dry run (no files written)")
    with col6:
        embed_images = st.checkbox(
            "Embed visual pages as PNG",
            help="Renders WAP/schedule pages as PNG images in the output (NOT anonymized).",
        )
    with col7:
        include_spreadsheets = st.checkbox(
            "Include CSV/XLSX",
            help="CSV/XLSX are excluded by default. Enable to anonymize them too.",
        )

    if st.button("Start Anonymization", type="primary", disabled=not (input_path and output_path)):
        input_p = Path(_clean_path(input_path))
        output_p = Path(_clean_path(output_path))

        if not input_p.exists():
            st.error(f"Input path does not exist: {input_p}")
        else:
            with st.spinner("Anonymizing…"):
                progress = st.progress(0, text="Initializing…")
                repo = _make_repo()
                uc = _make_anonymize_uc(repo)
                progress.progress(10, text="Pipeline ready — processing files…")
                result = uc.execute(
                    input_p, output_p,
                    recursive=recursive, force=force, dry_run=dry_run,
                    embed_images=embed_images, level=anon_level,
                    include_spreadsheets=include_spreadsheets,
                )
                progress.progress(100, text="Done.")

            st.success("Anonymization complete.")

            col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
            col_a.metric("Scanned", result.files_scanned)
            col_b.metric("New", result.files_new)
            col_c.metric("Changed", result.files_changed)
            col_d.metric("Skipped", result.files_skipped)
            col_e.metric("Errors", result.files_error)
            col_f.metric("Entities", result.entities_found)

            if result.warnings:
                with st.expander(f"⚠️ {len(result.warnings)} warning(s)"):
                    for w in result.warnings:
                        st.warning(w)

            if result.visual_page_count > 0:
                st.warning(
                    f"⚠ {result.visual_page_count} visual page(s) detected "
                    "(WAP/schedules). These are not extractable as text and have been "
                    "replaced with a placeholder marker in the output."
                )

            if dry_run:
                st.info("Dry run — no files were written.")


# ===========================================================================
# 🔓 De-Anonymize page
# ===========================================================================

elif page == "🔓 De-Anonymize":
    st.title("🔓 De-Anonymize Documents")
    st.markdown("Restore placeholders in LLM output files to their original values.")

    col1, col2 = st.columns(2)
    with col1:
        input_path = st.text_input(
            "Input folder or file",
            placeholder="/path/to/llm_output",
            help="Folder or single file with placeholders to restore.",
        )
    with col2:
        output_path = st.text_input(
            "Output folder",
            placeholder="/path/to/restored",
            help="Where de-anonymized files are written.",
        )

    col3, col4 = st.columns(2)
    with col3:
        force = st.checkbox("Force (reprocess all files)")
    with col4:
        dry_run = st.checkbox("Dry run (no files written)")

    if st.button(
        "Start De-Anonymization", type="primary", disabled=not (input_path and output_path)
    ):
        input_p = Path(_clean_path(input_path))
        output_p = Path(_clean_path(output_path))

        if not input_p.exists():
            st.error(f"Input path does not exist: {input_p}")
        else:
            with st.spinner("De-anonymizing…"):
                progress = st.progress(0, text="Initializing…")
                repo = _make_repo()
                uc = _make_deanonymize_uc(repo)
                progress.progress(10, text="Processing files…")
                result = uc.execute(input_p, output_p, force=force, dry_run=dry_run)
                progress.progress(100, text="Done.")

            st.success("De-anonymization complete.")

            col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
            col_a.metric("Scanned", result.files_scanned)
            col_b.metric("New", result.files_new)
            col_c.metric("Changed", result.files_changed)
            col_d.metric("Skipped", result.files_skipped)
            col_e.metric("Errors", result.files_error)
            col_f.metric("Resolved", result.placeholders_resolved)

            if result.warnings:
                with st.expander(f"⚠️ {len(result.warnings)} warning(s)"):
                    for w in result.warnings:
                        st.warning(w)

            if dry_run:
                st.info("Dry run — no files were written.")


# ===========================================================================
# 📄 DOCX Export page
# ===========================================================================

elif page == "📄 DOCX Export":
    st.title("📄 DOCX Export")
    st.markdown(
        "Convert anonymized Markdown to a formatted DOCX document "
        "using the official CH Armee Befehl template."
    )

    export_input = st.text_input(
        "Markdown-Datei (Pfad)",
        placeholder="/path/to/befehl.md",
        help="Path to the Markdown file to convert.",
        key="export_input",
    )

    col1, col2 = st.columns(2)
    with col1:
        export_template = st.selectbox(
            "Vorlage",
            ["Befehl (Einsatz)", "Befehl (Übung)"],
            key="export_template",
        )
    with col2:
        export_output = st.text_input(
            "Ausgabedatei (optional)",
            placeholder="auto: same name with .docx extension",
            key="export_output",
        )

    export_deanonymize = st.checkbox(
        "De-anonymisieren (Platzhalter → echte Namen)",
        value=True,
        key="export_deanonymize",
    )

    if st.button(
        "📄 DOCX generieren", type="primary", key="btn_export", disabled=not export_input
    ):
        try:
            from milanon.adapters.writers.docx_befehl_writer import DocxBefehlWriter
            from milanon.usecases.export_docx import ExportDocxUseCase

            in_path = Path(_clean_path(export_input))
            if not in_path.exists():
                st.error(f"File not found: {in_path}")
            else:
                tpl_name = (
                    "befehl_vorlage_uebung.docx"
                    if "Übung" in export_template
                    else "befehl_vorlage.docx"
                )
                tpl_path = _DATA_DIR / "templates" / "docx" / tpl_name

                if not tpl_path.exists():
                    st.error(f"Template not found: {tpl_path}")
                else:
                    out_path = (
                        Path(_clean_path(export_output))
                        if export_output.strip()
                        else in_path.with_suffix(".docx")
                    )

                    with st.spinner("Generating DOCX…"):
                        repo = _make_repo()
                        writer = DocxBefehlWriter()
                        uc = ExportDocxUseCase(repo, writer)
                        result_path = uc.execute(
                            in_path, out_path, tpl_path,
                            deanonymize=export_deanonymize,
                        )

                    st.success(f"DOCX generated: `{result_path}`")
                    if export_deanonymize:
                        st.info(
                            "De-anonymization applied — placeholders replaced with real values."
                        )

                    docx_bytes = Path(result_path).read_bytes()
                    st.download_button(
                        "⬇️ DOCX herunterladen",
                        data=docx_bytes,
                        file_name=Path(result_path).name,
                        mime=(
                            "application/vnd.openxmlformats-officedocument"
                            ".wordprocessingml.document"
                        ),
                    )
        except Exception as exc:
            st.error(f"Error: {exc}")


# ===========================================================================
# 📚 Doctrine Browser page
# ===========================================================================

elif page == "📚 Doctrine":
    st.title("📚 Doktrin-Datenbank")
    st.markdown(
        "Browse the Swiss Army doctrine knowledge base. "
        "These regulations power the 5+2 workflow prompts."
    )

    try:
        from milanon.usecases.doctrine import DoctrineExtractUseCase

        doctrine_uc = DoctrineExtractUseCase(_DATA_DIR / "doctrine")
        doctrine_files = doctrine_uc.list_doctrine_files()

        if not doctrine_files:
            st.warning("No doctrine files found in `data/doctrine/`.")
        else:
            st.subheader(f"{len(doctrine_files)} Reglemente")

            for doc in doctrine_files:
                title = doc.get("title", doc.get("filename", "Unknown"))
                regulation = doc.get("regulation", "")
                filename = doc.get("filename", "")
                chapters = doc.get("key_chapters", [])

                with st.expander(f"📖 {regulation} — {title}"):
                    st.caption(f"Datei: `data/doctrine/{filename}`")
                    if chapters:
                        st.markdown("**Kapitel:**")
                        for ch in chapters:
                            st.markdown(f"- {ch}")

                    # Show extract preview if available
                    extracts_dir = _DATA_DIR / "doctrine" / "extracts"
                    if extracts_dir.exists():
                        base = filename.replace(".md", "")
                        matching = list(extracts_dir.glob(f"*{base}*")) + list(
                            extracts_dir.glob(f"*{regulation.replace('.', '_')}*")
                        )
                        if matching:
                            st.markdown("**Verfügbare Extrakte:**")
                            for ext_path in sorted(set(matching)):
                                st.caption(f"`{ext_path.name}`")

        # Extract all button
        st.divider()
        extracts_dir = _DATA_DIR / "doctrine" / "extracts"
        existing_extracts = list(extracts_dir.glob("*.md")) if extracts_dir.exists() else []
        st.caption(f"{len(existing_extracts)} extract file(s) in `data/doctrine/extracts/`")

        if st.button("🔄 Alle Extrakte generieren", key="btn_extract_all"):
            with st.spinner("Extracting doctrine chapters…"):
                results = doctrine_uc.extract_all(extracts_dir)
            succeeded = sum(1 for v in results.values() if v)
            st.success(f"Extraction complete: {succeeded}/{len(results)} chapters extracted.")

    except Exception as exc:
        st.error(f"Error loading doctrine data: {exc}")


# ===========================================================================
# 🚀 Project Generator page
# ===========================================================================

elif page == "🚀 Project Generator":
    st.title("🚀 Claude Project Generator")
    st.markdown(
        "Generate a ready-to-import Claude.ai Project folder with "
        "system prompt, doctrine knowledge, and workflow instructions."
    )

    proj_unit = st.text_input(
        "Einheit",
        value=_get_config_value("unit", ""),
        placeholder='z.B. "Inf Kp 56/1"',
        key="proj_unit",
    )

    proj_input = st.text_input(
        "Anonymisierte Dokumente (optional)",
        value="",
        placeholder="/path/to/anonymized/output",
        key="proj_input",
        help="Pfad zu anonymisierten Dateien — werden in knowledge/ kopiert.",
    )

    col_proj1, col_proj2 = st.columns(2)
    with col_proj1:
        proj_output = st.text_input(
            "Ausgabeordner",
            value=str(Path.home() / "claude_project"),
            key="proj_output",
        )
    with col_proj2:
        proj_include_images = st.checkbox(
            "Bilder einbinden (PNG)",
            key="proj_images",
            help="WAP/Karten als PNG-Dateien in knowledge/ kopieren.",
        )

    if st.button(
        "🚀 Projekt generieren",
        type="primary", key="btn_proj", disabled=not (proj_unit and proj_output),
    ):
        try:
            from milanon.usecases.generate_project import GenerateProjectUseCase

            uc = GenerateProjectUseCase(_DATA_DIR)
            input_p = Path(_clean_path(proj_input)) if proj_input.strip() else None
            result = uc.execute(
                proj_unit.strip(), Path(_clean_path(proj_output)),
                input_path=input_p, include_images=proj_include_images,
            )

            st.success(f"Project generated for: **{result.unit}**")
            st.markdown(f"Output: `{result.output_dir}`")

            with st.expander(f"📁 {len(result.files_created)} files created"):
                for f in result.files_created:
                    st.caption(f"→ `{f}`")

            # Offer ZIP download
            import io
            import zipfile

            zip_buffer = io.BytesIO()
            project_dir = Path(result.output_dir)
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in sorted(project_dir.rglob("*")):
                    if file_path.is_file():
                        zf.write(file_path, file_path.relative_to(project_dir.parent))
            zip_buffer.seek(0)

            st.download_button(
                "⬇️ ZIP herunterladen",
                data=zip_buffer.getvalue(),
                file_name=(
                    "claude_project_"
                    + proj_unit.strip().replace(" ", "_").replace("/", "_")
                    + ".zip"
                ),
                mime="application/zip",
            )

        except Exception as exc:
            st.error(f"Error: {exc}")

    st.info("Das generierte Projekt kann direkt in Claude.ai importiert werden.")


# ===========================================================================
# 📥 DB Import page
# ===========================================================================

elif page == "📥 DB Import":
    st.title("📥 Import Personnel Data")
    st.markdown(
        "Upload a CSV file to pre-populate the mapping database. "
        "Known entities will be detected more accurately during anonymization."
    )

    import_format = st.radio(
        "Import Format",
        ["PISA 410 / MilOffice", "Simple Name List (Grad;Vorname;Nachname)"],
        horizontal=True,
    )

    if import_format == "PISA 410 / MilOffice":
        st.caption(
            "PISA 410 format: row 1 = title, row 2 = headers, rows 3+ = data. Semicolon-delimited."
        )
    else:
        st.caption(
            "Simple format: header row `Grad;Vorname;Nachname`,"
            " one person per row. Grad is optional."
        )

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded is not None and st.button("Import", type="primary"):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(uploaded.read())
            tmp_path = Path(tmp.name)

        with st.spinner("Importing…"):
            from milanon.domain.mapping_service import MappingService

            repo = _make_repo()
            service = MappingService(repo)

            if import_format == "Simple Name List (Grad;Vorname;Nachname)":
                from milanon.usecases.import_names import ImportNamesUseCase
                uc = ImportNamesUseCase(service)
            else:
                from milanon.usecases.import_entities import ImportEntitiesUseCase
                uc = ImportEntitiesUseCase(service)

            result = uc.execute(tmp_path, source_document=uploaded.name)

        tmp_path.unlink(missing_ok=True)

        st.success("Import complete.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows processed", result.rows_processed)
        col2.metric("Rows skipped", result.rows_skipped)
        col3.metric("Entities imported", result.entities_imported)

    # -----------------------------------------------------------------------
    # Quick Add — Single Person
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Quick Add — Single Person")
    st.caption("Add one person directly without a CSV file.")

    qa_col1, qa_col2, qa_col3 = st.columns(3)
    with qa_col1:
        qa_grad = st.text_input("Grad", placeholder="z.B. Hptm", key="qa_grad")
    with qa_col2:
        qa_vorname = st.text_input("Vorname", placeholder="z.B. Thomas", key="qa_vorname")
    with qa_col3:
        qa_nachname = st.text_input("Nachname", placeholder="z.B. Wegmüller", key="qa_nachname")

    if st.button("Add Person", key="qa_add"):
        qa_vorname_v = qa_vorname.strip()
        qa_nachname_v = qa_nachname.strip()
        qa_grad_v = qa_grad.strip()

        if not qa_vorname_v or not qa_nachname_v:
            st.warning("Vorname and Nachname are required.")
        else:
            from milanon.domain.entities import EntityType
            from milanon.domain.mapping_service import MappingService

            repo = _make_repo()
            service = MappingService(repo)

            full_name = f"{qa_vorname_v} {qa_nachname_v.upper()}"
            already_exists = repo.get_mapping(EntityType.PERSON, full_name) is not None

            if already_exists:
                st.info(f"Already exists in database: {full_name}")
            else:
                count = 0
                service.get_or_create_placeholder(EntityType.PERSON, full_name)
                count += 1
                service.get_or_create_placeholder(EntityType.VORNAME, qa_vorname_v)
                count += 1
                service.get_or_create_placeholder(EntityType.NACHNAME, qa_nachname_v)
                count += 1
                if qa_grad_v:
                    service.get_or_create_placeholder(EntityType.GRAD_FUNKTION, qa_grad_v)
                    count += 1
                label = f"{qa_grad_v} {full_name}".strip() if qa_grad_v else full_name
                st.success(f"Added: {label} ({count} entities)")
                st.session_state["qa_grad"] = ""
                st.session_state["qa_vorname"] = ""
                st.session_state["qa_nachname"] = ""
                st.rerun()


# ===========================================================================
# 📊 DB Stats page
# ===========================================================================

elif page == "📊 DB Stats":
    st.title("📊 Database Statistics")
    st.markdown(f"Database: `{Path.home() / '.milanon' / 'milanon.db'}`")

    repo = _make_repo()

    # Check if reference data is loaded
    ref_muni_count = repo.get_ref_municipality_count()
    ref_mil_count = repo.get_ref_military_unit_count()

    if ref_muni_count == 0 or ref_mil_count == 0:
        st.warning(
            "⚠️ Reference data not loaded (municipalities and/or military units missing)."
        )
        if st.button("🔄 Initialize Reference Data", type="primary"):
            with st.spinner("Loading reference data…"):
                init_result = _init_reference_data(repo)
            st.success(
                f"✅ Initialized: {init_result.municipalities_loaded} municipalities, "
                f"{init_result.military_units_loaded} military units."
            )
            st.rerun()
    else:
        st.caption(
            f"Reference data: {ref_muni_count} municipalities, {ref_mil_count} military units ✅"
        )

    total = repo.get_total_mapping_count()
    by_type = repo.get_mapping_count_by_type()

    st.metric("Total entities", total)

    if by_type:
        st.subheader("Entities by type")
        rows = sorted(by_type.items())
        st.dataframe(
            {"Entity Type": [r[0] for r in rows], "Count": [r[1] for r in rows]},
            use_container_width=True,
            hide_index=True,
        )

        import pandas as pd
        df = pd.DataFrame(rows, columns=["Type", "Count"]).set_index("Type")
        st.bar_chart(df)
    else:
        st.info("Database is empty. Import a PISA CSV or run anonymization to populate it.")

    # -----------------------------------------------------------------------
    # Database Management
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Database Management")

    col_reset, col_full = st.columns(2)

    with col_reset:
        st.warning(
            "**Reset Mappings** — deletes all entity mappings and file tracking."
            " Reference data (municipalities, military units) is preserved."
        )
        confirm_reset = st.checkbox("I confirm: delete all mappings", key="confirm_reset")
        if st.button("Reset Mappings", disabled=not confirm_reset, key="btn_reset"):
            counts = repo.reset_all_mappings()
            st.success(
                f"Mappings reset. {counts['entity_mappings']} mappings and "
                f"{counts['file_tracking']} tracking records deleted."
            )
            st.rerun()

    with col_full:
        st.error(
            "**Reset Everything** — deletes ALL data including reference data."
            " Reference data will be re-initialized automatically."
        )
        confirm_full = st.checkbox(
            "I confirm: delete everything including reference data", key="confirm_full"
        )
        if st.button("Reset Everything", disabled=not confirm_full, key="btn_full_reset"):
            counts = repo.reset_everything()
            total_deleted = sum(counts.values())
            init_result = _init_reference_data(repo)
            st.success(
                f"Full reset complete. {total_deleted} rows deleted. "
                f"Re-initialized: {init_result.municipalities_loaded} municipalities, "
                f"{init_result.military_units_loaded} military units."
            )
            st.rerun()


# ===========================================================================
# ⚙️ Config page
# ===========================================================================

elif page == "⚙️ Config":
    st.title("⚙️ Konfiguration")
    st.markdown(
        f"Settings are saved to `{_CONFIG_PATH}` and persist across sessions."
    )

    current_config = _load_config()

    cfg_mode = st.radio(
        "Standard-Modus",
        ["berrm", "adf"],
        index=0 if current_config.get("mode", "berrm") == "berrm" else 1,
        horizontal=True,
        key="cfg_mode",
    )

    cfg_level = st.radio(
        "Standard-Anonymisierungsstufe",
        ["dsg", "full"],
        index=0 if current_config.get("level", "dsg") == "dsg" else 1,
        horizontal=True,
        key="cfg_level",
        help="DSG = nur Personendaten (DSGVO), Full = alle Entitäten inkl. Einheiten/Orte",
    )

    cfg_unit = st.text_input(
        "Standard-Einheit",
        value=current_config.get("unit", ""),
        placeholder='z.B. "Inf Kp 56/1"',
        key="cfg_unit",
    )

    if st.button("💾 Speichern", type="primary", key="btn_cfg_save"):
        new_config = _load_config()
        new_config["mode"] = cfg_mode
        new_config["level"] = cfg_level
        if cfg_unit.strip():
            new_config["unit"] = cfg_unit.strip()
        elif "unit" in new_config:
            del new_config["unit"]
        _save_config(new_config)
        st.success("Konfiguration gespeichert.")

    st.divider()
    st.subheader("Aktuelle Konfiguration")
    if current_config:
        for k, v in sorted(current_config.items()):
            st.code(f"{k} = {v}")
    else:
        st.caption("Keine Konfiguration gesetzt.")
