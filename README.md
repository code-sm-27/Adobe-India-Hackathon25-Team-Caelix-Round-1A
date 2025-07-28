# Adobe Hackathon 2025: Document Outline Extractor

This project is a solution for the Round 1A challenge. It intelligently parses PDF documents to extract a structured outline, including the main title and a hierarchy of headings (H1, H2, H3).

### **Our Approach**

The core of this solution is a robust, dual-strategy parser designed to handle a wide variety of document layouts while respecting the competition's strict performance and size constraints.

1.  **Typographical Profiling:** The script first performs a quick analysis of the entire document to determine the most common font size, which serves as a reliable baseline for the "body text."

2.  **Intelligent Title Extraction:** A scoring-based engine identifies the document's main title. It analyzes text in the top portion of the first page, scoring candidates based on a combination of their font size, boldness, and horizontal centering. This allows it to distinguish the true title from other text.

3.  **Dual-Strategy Heading Detection:** To maximize accuracy, the parser attacks the problem from two directions simultaneously:
    * **Pattern-Based Detection:** It uses regular expressions to find headings that follow common structural patterns, such as numbered or lettered lists (`1.`, `2.1`, `Appendix A:`). This is highly effective for technical documents and formal reports.
    * **Style-Based Detection:** It identifies headings based on visual style—specifically, text that is bold and significantly larger than the document's body text. This captures headings in less formally structured documents, like flyers.

4.  **Finalization:** The results from both strategies are merged, deduplicated, and sorted by their position in the document to produce a clean and accurate final outline.

This hybrid approach ensures the solution is both resilient and precise, delivering high-quality outlines across diverse PDF formats.

### **Libraries Used**

* **`PyMuPDF`**: A lightweight and high-performance library for all PDF parsing and text extraction needs. No other external models or large libraries are used.

### **How to Build and Run**

1.  **Build the Docker Image:**
    ```bash
    docker build --platform linux/amd64 -t my-r1a-solution:latest .
    ```

2.  **Run the Docker Container:**
    ```bash
    docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none my-r1a-solution:latest
    ```
