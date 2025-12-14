# 10-K SEC Filings RAG System

A pipeline for extracting, preprocessing, and chunking 10-K SEC filings into a vector database for Retrieval-Augmented Generation (RAG) systems.

---

## Assumptions

### 1. **Client Requirements: Actual 10-K Text Only**
We assume the client only needs the actual 10-K document text, excluding:
- Cover pages and front matter
- Table of Contents
- Exhibits and Schedules (Items 15 and beyond)
- Supplementary documents and attachments

The focus is on extracting the core business, financial, and management disclosures (Items 1-14).

### 2. **Manual 10-K Parsing**
We assume manual parsing of the 10-K structure is intentional and in scope for this project, despite existing EDGAR parsing libraries and tools. This approach provides:
- Fine-grained control over preprocessing
- Deeper understanding of SEC filing structure
- Ability to handle edge cases and formatting inconsistencies across different filers
- Customization for RAG-specific text extraction and chunking

### 3. *[Additional assumptions to be documented]*

---

## Project Structure

### Folder Hierarchy

```
10-K_RAG/
├── data/
│   ├── sec-edgar-filings/          # Raw 10-K filings from SEC EDGAR
│   │   ├── AAPL/
│   │   ├── AMZN/
│   │   ├── GOOGL/
│   │   ├── MSFT/
│   │   └── NVDA/
│   └── processed_filings/          # Cleaned, preprocessed 10-K documents
├── notebooks/                      # Jupyter notebooks for initial prototyping stage
│   ├── get_data.ipynb              
│   ├── preprocess.ipynb            
│   ├── chunk.ipynb                 
├── scripts/                        # Actual production scripts when prototyping is over
│   ├── utils.py                    # Shared utilities (ITEM_PATTERNS, helpers)
│   └── __pycache__/
├── readme.md
```

---

## Notebooks & Pipeline

### 1. **get_data.ipynb**
*Purpose:* Download 10-K filings from SEC EDGAR

**Key Steps:**
1. **Load Configuration** - Reads ticker list, company name, and email from `cfg.json`
2. **Ensure Directory Exists** - Creates the destination folder if it doesn't already exist using `os.makedirs()`
3. **Download Filings** - Uses `sec_edgar_downloader` to fetch 10-K filings for specified tickers
   - Filters for 10-K documents filed after January 1, 2024
   - Downloads raw SGML/HTML filing documents

**Output:** Raw SGML/HTML filing documents in the configured destination folder

---

### 2. **preprocess.ipynb**
*Purpose:* Clean and standardize raw 10-K documents

**Key Steps:**
1. **Extract 10-K Document** - Isolates the actual 10-K text from SGML wrapper
2. **Convert Tables to Text** - Uses `table_to_text()` to transform HTML tables into readable prose:
   - Merges currency symbols (`$`) with numbers
   - Merges percentages (`%`) with values
   - Preserves ITEM headers found in tables (handles Amazon's nested tables)
3. **Remove Scripts/Styles** - Strips HTML scripts and stylesheets
4. **Normalize Text** - Replaces non-breaking spaces, consolidates whitespace

**Output:** Cleaned plain text documents in `data/processed_filings/`

---

### 3. **chunk.ipynb**
*Purpose:* Extract sections, create RAG-ready chunks, and upsert to Pinecone

**Key Steps:**
1. **Load Processed Documents** - Reads cleaned 10-K documents from `processed_data_folder`
2. **Smart TOC Detection** - Identifies actual document start (skips table of contents):
   - Finds all ITEM 1 and ITEM 1A positions
   - Verifies real content by checking if section size between ITEM 1 and ITEM 1A > 5K chars
   - Falls back to first match if size verification fails
3. **Section Extraction** - Identifies all ITEM sections (Item 1-15) and their positions
4. **Chunking with Overlap** - Splits each section into overlapping chunks:
   - Default chunk size: 400 words
   - Default overlap: 50 words
5. **Metadata Attachment** - Each chunk includes:
   - Chunk ID: `{ticker}_{fiscal_year}_chunk{number}`
   - Chunk text with ITEM name prepended
   - Ticker symbol
   - Fiscal year
   - Item ID (e.g., `item_1`, `item_7`)
   - Chunk size (in characters)
6. **Pinecone Integration** - Creates and manages two indices:
   - **Dense Index** (`10k-dense`): Uses Llama text embeddings for semantic search
   - **Sparse Index** (`10k-sparse`): Uses Pinecone sparse embeddings for keyword search
   - Upserts chunks in batches of 96 records with 13-second delays between batches

**Output:** Chunks embedded and stored in both dense and sparse Pinecone indices

---

### 4. **get_filings copy.ipynb**
*Purpose:* Testing/experimentation notebook

**Status:** Development/testing stage

---

## Key Components

### `utils.py`
Shared utilities module containing:
- **`ITEM_PATTERNS`** - Regex patterns for all 15 10-K items with flexible matching
  - Handles variations: `ITEM 1.`, `Item 1A.`, `Item&nbsp;1B.` (with non-breaking spaces)
  - Optional descriptive text after item number
  - Case-insensitive matching

### Core Functions
- **`table_to_text(table)`** - Converts HTML tables to readable text while preserving structure and labels
- **`clean(cell)`** - Normalizes individual cell text (removes non-breaking spaces, consolidates whitespace)
- **`process_doc(doc)`** - Main preprocessing pipeline for raw 10-K documents
- **`chunk_10k(text, ticker, fiscal_year, chunk_size=400, overlap=50)`** - Intelligent chunking with TOC detection and metadata attachment

---

## Data Flow

```
Raw SGML Filing
    ↓
[get_data.ipynb] → Download from SEC EDGAR
    ↓
[preprocess.ipynb] → Clean, convert tables, normalize
    ↓
[chunk.ipynb] → Extract sections, create chunks with metadata and upsert to Pinecone
    ↓
TBD
```

---

## Future Enhancements

- TBD

---

## Disclaimer

This README was written with the assistance of AI.
