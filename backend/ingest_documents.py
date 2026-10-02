from pathlib import Path
import json
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
OUTPUT_FILE = PROJECT_ROOT / "data" / "documents_metadata.json"


def extract_metadata(content):
    metadata = {}

    fields = [
        "Document Title",
        "Document Type",
        "Version",
        "Date",
        "Owner",
        "Approving Authority",
        "Related Documents",
        "Classification",
        "Category",
        "Review Frequency",
        "Repository Path",
        "Confidentiality",
        "License"
    ]

    for field in fields:
        pattern = rf"\*\*{re.escape(field)}:\*\*\s*(.+?)(?:\\)?$"

        match = re.search(
            pattern,
            content,
            re.MULTILINE
        )

        if match:
            value = match.group(1).strip()

            # Remove trailing Markdown escape
            value = value.rstrip("\\")

            metadata[field] = value

    return metadata


def detect_document_type(filename):
    name = filename.lower()

    if name.startswith("policy-"):
        return "policy"

    if name.startswith("procedure-"):
        return "procedure"

    if name.startswith("standard-"):
        return "standard"

    if name.startswith("framework-"):
        return "framework"

    if name.startswith("sop-"):
        return "sop"

    if name.startswith("roadmap-"):
        return "roadmap"

    return "other"


def extract_sections(content):
    lines = content.splitlines()

    sections = []

    current_heading = None
    current_level = None
    current_content = []

    for line in lines:

        heading_match = re.match(
            r"^(#{1,6})\s+(.+?)\s*$",
            line
        )

        if heading_match:

            if current_heading is not None:

                section_text = "\n".join(
                    current_content
                ).strip()

                if section_text:
                    sections.append({
                        "heading": current_heading,
                        "level": current_level,
                        "text": section_text
                    })

            current_level = len(
                heading_match.group(1)
            )

            current_heading = (
                heading_match.group(2).strip()
            )

            current_content = []

        else:
            current_content.append(line)

    # Add final section
    if current_heading is not None:

        section_text = "\n".join(
            current_content
        ).strip()

        if section_text:
            sections.append({
                "heading": current_heading,
                "level": current_level,
                "text": section_text
            })

    return sections


def process_document(file_path):

    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    metadata = extract_metadata(content)

    sections = extract_sections(content)

    document = {
        "document_id": file_path.stem,
        "filename": file_path.name,

        "document_title": metadata.get(
            "Document Title"
        ),

        "document_type": metadata.get(
            "Document Type",
            detect_document_type(file_path.name)
        ),

        "version": metadata.get(
            "Version"
        ),

        "date": metadata.get(
            "Date"
        ),

        "owner": metadata.get(
            "Owner"
        ),

        "approving_authority": metadata.get(
            "Approving Authority"
        ),

        "related_documents": metadata.get(
            "Related Documents"
        ),

        "classification": metadata.get(
            "Classification"
        ),

        "category": metadata.get(
            "Category"
        ),

        "review_frequency": metadata.get(
            "Review Frequency"
        ),

        "repository_path": metadata.get(
            "Repository Path"
        ),

        "confidentiality": metadata.get(
            "Confidentiality"
        ),

        "license": metadata.get(
            "License"
        ),

        "character_count": len(content),

        "word_count": len(
            content.split()
        ),

        "section_count": len(
            sections
        ),

        "sections": sections
    }

    return document


def main():

    files = sorted(
        DOCUMENTS_DIR.glob("*.md")
    )

    print(
        f"Documents found: {len(files)}"
    )

    documents = []

    for file_path in files:

        document = process_document(
            file_path
        )

        documents.append(document)

        print(
            f"{file_path.name} | "
            f"{document['document_type']} | "
            f"{document['section_count']} sections | "
            f"{document['word_count']} words"
        )

    OUTPUT_FILE.write_text(
        json.dumps(
            documents,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    total_sections = sum(
        document["section_count"]
        for document in documents
    )

    total_words = sum(
        document["word_count"]
        for document in documents
    )

    print()
    print("========== DATASET SUMMARY ==========")
    print(
        f"Documents: {len(documents)}"
    )
    print(
        f"Sections: {total_sections}"
    )
    print(
        f"Words: {total_words}"
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()