"""MilAnon Streamlit GUI — local browser interface for anonymization."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import streamlit as st

# Path to bundled reference data
_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _clean_path(raw: str) -> str:
    """Strip surrounding whitespace and single/double quotes from a path input."""
    return raw.strip().strip("'\"")


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
    ["Anonymize", "De-Anonymize", "LLM Workflow", "DB Import", "DB Stats"],
    index=0,
)

st.sidebar.divider()
st.sidebar.caption("All processing is local. No data leaves your machine.")
from milanon import __version__
st.sidebar.caption(f"Version {__version__}")


# ---------------------------------------------------------------------------
# Anonymize page
# ---------------------------------------------------------------------------

if page == "Anonymize":
    st.title("Anonymize Documents")
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

    col3, col4, col5, col6 = st.columns(4)
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
                    recursive=recursive, force=force, dry_run=dry_run, embed_images=embed_images,
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


# ---------------------------------------------------------------------------
# De-Anonymize page
# ---------------------------------------------------------------------------

elif page == "De-Anonymize":
    st.title("De-Anonymize Documents")
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

    if st.button("Start De-Anonymization", type="primary", disabled=not (input_path and output_path)):
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


# ---------------------------------------------------------------------------
# LLM Workflow page
# ---------------------------------------------------------------------------

elif page == "LLM Workflow":
    st.title("LLM Workflow")
    st.markdown(
        "Prepare context for Claude, work with the LLM, then restore real names from the response."
    )

    tab1, tab2, tab3 = st.tabs(["1. Generate Context", "2. Send to LLM", "3. Unpack Response"])

    # -------------------------------------------------------------------
    # Tab 1 — Generate Context
    # -------------------------------------------------------------------
    with tab1:
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
                value="test_output/CONTEXT.md",
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

        # -------------------------------------------------------------------
        # Pack Builder
        # -------------------------------------------------------------------
        st.divider()
        st.subheader("Pack Builder")
        st.markdown(
            "Assemble context + template + anonymized documents into a single clipboard-ready prompt."
        )

        from milanon.usecases.pack import PackUseCase, list_templates as _list_templates

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

        if st.button("Build Pack & Copy to Clipboard", type="primary", key="btn_pack", disabled=not pack_input):
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
    # Tab 2 — Send to LLM
    # -------------------------------------------------------------------
    with tab2:
        st.subheader("Work with Claude.ai")
        st.markdown(
            """
**Steps:**
1. Generate your context file (Tab 1) — or use Pack Builder to assemble everything at once.
2. Open [Claude.ai](https://claude.ai) in your browser.
3. Paste the pack (or context + anonymized document) into the prompt.
4. Work with Claude — ask it to create notes, analyze, draft orders.
5. Copy Claude's response and paste it in Tab 3 to restore real names.
            """
        )
        st.info(
            "💡 Tip: Use Pack Builder in Tab 1 to assemble context + template + documents "
            "into a single clipboard-ready prompt."
        )

    # -------------------------------------------------------------------
    # Tab 3 — Unpack Response
    # -------------------------------------------------------------------
    with tab3:
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
                    with st.expander(f"⚠️ {len(unpack_result.warnings)} unresolved placeholder(s)"):
                        for w in unpack_result.warnings:
                            st.warning(w)
            except Exception as exc:
                st.error(f"Error: {exc}")


# ---------------------------------------------------------------------------
# DB Import page
# ---------------------------------------------------------------------------

elif page == "DB Import":
    st.title("Import Personnel Data")
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
        st.caption("PISA 410 format: row 1 = title, row 2 = headers, rows 3+ = data. Semicolon-delimited.")
    else:
        st.caption("Simple format: header row `Grad;Vorname;Nachname`, one person per row. Grad is optional.")

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded is not None:
        if st.button("Import", type="primary"):
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


# ---------------------------------------------------------------------------
# DB Stats page
# ---------------------------------------------------------------------------

elif page == "DB Stats":
    st.title("Database Statistics")
    st.markdown(f"Database: `{Path.home() / '.milanon' / 'milanon.db'}`")

    repo = _make_repo()

    # Check if reference data is loaded
    ref_muni_count = repo.get_ref_municipality_count()
    ref_mil_count = repo.get_ref_military_unit_count()

    if ref_muni_count == 0 or ref_mil_count == 0:
        st.warning("⚠️ Reference data not loaded (municipalities and/or military units missing).")
        if st.button("🔄 Initialize Reference Data", type="primary"):
            with st.spinner("Loading reference data…"):
                init_result = _init_reference_data(repo)
            st.success(
                f"✅ Initialized: {init_result.municipalities_loaded} municipalities, "
                f"{init_result.military_units_loaded} military units."
            )
            st.rerun()
    else:
        st.caption(f"Reference data: {ref_muni_count} municipalities, {ref_mil_count} military units ✅")

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
        st.warning("**Reset Mappings** — deletes all entity mappings and file tracking. Reference data (municipalities, military units) is preserved.")
        confirm_reset = st.checkbox("I confirm: delete all mappings", key="confirm_reset")
        if st.button("Reset Mappings", disabled=not confirm_reset, key="btn_reset"):
            counts = repo.reset_all_mappings()
            st.success(
                f"Mappings reset. {counts['entity_mappings']} mappings and "
                f"{counts['file_tracking']} tracking records deleted."
            )
            st.rerun()

    with col_full:
        st.error("**Reset Everything** — deletes ALL data including reference data. Reference data will be re-initialized automatically.")
        confirm_full = st.checkbox("I confirm: delete everything including reference data", key="confirm_full")
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
