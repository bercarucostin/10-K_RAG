# 10-K SEC Filings RAG System

A pipeline for extracting, preprocessing, and chunking 10-K SEC filings into a vector database for Retrieval-Augmented Generation (RAG) systems.

---

## Assumptions

### 1. **Client Requirements: Actual 10-K Text Only**
We assume the client only needs the **actual 10-K document text**, excluding:
- Cover pages and front matter
- Table of Contents
- Exhibits and Schedules (Items 15 and beyond)
- Supplementary documents and attachments

The focus is on extracting the core business, financial, and management disclosures (Items 1-14). These things would, in a real life situation, be clarified with the client before the start of the actual implementation.

### 2. **Manual 10-K Parsing**
We assume manual parsing of the 10-K structure is intentional and in scope for this project, despite existing EDGAR parsing libraries and tools. This approach provides:
- Fine-grained control over preprocessing
- Deeper understanding of SEC filing structure
- Ability to handle edge cases and formatting inconsistencies across different filers
- Customization for RAG-specific text extraction and chunking

### 3. **This is just a PoC**
We assume the client first wants to make sure that such an idea would work and to get an assumption of the costs. There are multiple possible improvements over the current solution which will be detailed further below.

---

## Costs

### 1. **Pinecone**

- **Free until we need more than 2GB of storage, 2M writes per month or 1M reads per month. BUT we don't have backups (unless we keep physical backups for the raw processed filings ourselves), we can only use 5 indexes and 100 namespaces per index. None of these should be a problem for the task at hand. We presume we only need to insert 10-K filings into Pinecone (they are filed once yearly for each company)**
- **Storage**: For 5 companies and 2 years of filings we needed 5MB of data. This is while keeping both a dense and a sparse index! We could store 400x more data and still barely reach the limit. If the client wants to focus on a few specific companies, this will not be a problem for the forseable future. We could store data about 500 companies yearly while keeping the history for the last 7 years (+ the current one) and still barely hit the limit. It's improbable that this is the metric that will tip us towards needing a paid plan.
- **Writes**: Pinecone charges 1 WU (write unit) per KB of data uploaded and offers 2M free write units per month. This means we could write 2GB (the whole storage) each month if we would need to. We already clarified that the whole 2GB storage is an immense ammount of storage for our yearly 10-K needs. Even taking into account that at some point we will need to clean historical data with deletes which also cost write units, it is improbable that this limit will hinder the project for the forseable future.
- **Reads**: Pinecone explains how it charges RUs (read units) for the Query/Fetch/List methods, but not for Search which is the method we actually use. Judging by the low number of RU used in this project until now, we will presume it is similar to the "Query" pricing. Let's take the worst case where our namespace is full. This means each search takes 2 RUs. With a monthly limit of 1M RUs, this means that a team of 23 people could submit ~1000 queries (searches) per day for an average of 21 working days per month and we would be within the allowed limit. This may be the limit that could eventually put us over the free plan, but not too soon.
- **The first paid plan, the Standard version has a minimum cost of $50 per month. The most expensive thing are the RU, which cost $16 per milion. If we eventually have a team of 100 people that use 1000 queries a day for an average of 21 working days per month we could still stay well within $100 per month.**

### 2. **Gemini**

- **We use Gemini AI as our chatbot. If we wish to continue using Gemini 2.5 Flash-Lite OR Gemini 2.5 Pro, these models are free of charge with no limits on usage ON THE CONDITION Google uses our usage of the models to improve their products. If this is okay with our client, we could stay on the Free Tier and use these models for the forseeable future. If not:**
- **Writes**: On the Paid Tier, Gemini 2.5 Flash-Lite costs $0.40 per 1M output tokens. If we presume an average response length of 500 tokens/words (which is a pessimistic assumption) then it would cost $100 per month for the LLM to answer a team of 23 people at a rate of 1000 queries per day for an average of 21 working days per month.
- **Reads**: On the Paid Tier, Gemini 2.5 Flash-Lite costs $0.10 per 1M input tokens. The chunks from our retriever have 400 tokens each. Let's assume we feed the model a query of maximum 100 tokens and 5 chunks (2000 tokens) each time we ask a question. This means 2100 read tokens per question. It would cost $100 per month for a team of 23 people asking questions at a rate of 1000 queries per day for an average of 21 working days per month.

### 3. **Conclusion**
**We could stay on the free tier of Pinecone and pay ~$200 a month to Google for Gemini in order to succesfully serve a team of 23 people asking questions at a rate of 1000 queries per day for an average of 21 working days per month.**

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
│   ├── chatbot.ipynb
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
2. **Ensure Directory Exists** - Creates the destination folder if it doesn't already exist 
3. **Download Filings** - Uses `sec_edgar_downloader` to fetch 10-K filings for specified tickers
   - Filters for 10-K documents filed after January 1, 2024
   - Downloads raw SGML/HTML filing documents

**Output:** Raw SGML/HTML filing documents in the configured destination folder

---

### 2. **preprocess.ipynb**
*Purpose:* Clean and standardize raw 10-K documents

**Key Steps:**
1. **Extract 10-K Document** - Isolates the actual 10-K text from SGML wrapper
2. **Convert Tables to Text** - Uses `table_to_text()` to transform HTML tables into meaningful text
3. **Remove Scripts/Styles** - Strips HTML scripts and stylesheets
4. **Normalize Text** - Replaces non-breaking spaces, consolidates whitespace

**Output:** Cleaned plain text documents in `data/processed_filings/`

---

### 3. **chunk.ipynb**
*Purpose:* Extract sections, create RAG-ready chunks, and upsert to Pinecone

**Key Steps:**
1. **Load Processed Documents** - Reads cleaned 10-K documents from `processed_data_folder`
2. **Smart TOC Detection** - Identifies actual document start (skips table of contents)
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

**Output:** Chunks embedded and stored in both dense and sparse Pinecone indices

---

### 4. **chatbot.ipynb**
*Purpose:* RAG-based chatbot for querying financial information from 10-K filings

**Key Steps:**
1. **Initialize Clients** - Sets up Pinecone indices and Gemini client
2. **Ticker Detection** - Detects mentioned companies from user query
3. **Selective Retrieval** - Searches only detected company filings, or all if none detected:
   - Returns top 20 results if company detected
   - Returns top 30 results if searching all companies
4. **Result Enrichment** - Formats retrieved chunks with company name and fiscal year context
5. **LLM Generation** - Uses Gemini to generate answers with:
   - System instruction: Financial expert assistant who supports claims with direct quotes
   - Temperature: 0.5 (more deterministic)
6. **Logging** - Appends each interaction to CSV log with:
   - `timestamp`: Query execution time
   - `query`: User's question
   - `tickers`: Detected companies
   - `retriever_results`: Retrieved context from filings
   - `llm_answer`: Generated response

**Output:** 
- Console output of LLM answer
- Appended row in `log.csv` with complete interaction data

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
[chatbot.ipynb] → Query user question → Retrieve relevant chunks → Generate answer → Log interaction
    ↓
log.csv (Interaction history with query, retriever results, and LLM answers)
```

---Usage

### Running the Chatbot

```python
# Initialize clients and indices (run setup cells first)
response = chat(
    query="Compare Amazon's and Nvidia's operating risks.",
    dense_index=dense_index,
    sparse_index=sparse_index,
    genai_client=client,
    log_path='../log.csv'
)
print(response)
```

The function will:
1. Automatically detect mentioned companies
2. Retrieve relevant sections from their 10-K filings
3. Generate a financial expert response
4. Log the complete interaction (query, results, answer, timestamp) to the CSV file

## Future Developments

- **Most importantly: Get Customer Feedback on prototype!!**
- Give access to a few members of the client's team and observe their usage (from the logs) and gather feedback. Bring improvements to the prototype if necessary
- Move everything from notebooks (prototyping phase) into scripts (production phase)
- Improve 10-K parsing and chunking
- Add support for sparse index retrieval alongside dense index
- Implement and measure Retriever performance metrics (precision/recall) and decide on the best configuration of index and parameters
- Use ragas to evaluate LLM performance. Adjust temperature and system prompt.
- Implement conversation history/context for multi-turn queries

---

## Disclaimer

This README was written with the assistance of AI.
