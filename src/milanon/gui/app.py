"""MilAnon Streamlit GUI — local browser interface for anonymization."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import streamlit as st


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
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    csv_path = data_dir / "swiss_municipalities.csv"
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


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🔒 MilAnon")
st.sidebar.markdown("Swiss Military Document Anonymizer")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Anonymize", "De-Anonymize", "DB Import", "DB Stats"],
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

    col3, col4, col5 = st.columns(3)
    with col3:
        recursive = st.checkbox("Recursive (include subfolders)")
    with col4:
        force = st.checkbox("Force (reprocess all files)")
    with col5:
        dry_run = st.checkbox("Dry run (no files written)")

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
                result = uc.execute(input_p, output_p, recursive=recursive, force=force, dry_run=dry_run)
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
                # Clear fields via session state
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

        # Bar chart
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
        st.error("**Reset Everything** — deletes ALL data including reference data. You will need to run `milanon db init` afterward.")
        confirm_full = st.checkbox("I confirm: delete everything including reference data", key="confirm_full")
        if st.button("Reset Everything", disabled=not confirm_full, key="btn_full_reset"):
            counts = repo.reset_everything()
            total = sum(counts.values())
            st.success(f"Full reset complete. {total} rows deleted across all tables.")
            st.rerun()
