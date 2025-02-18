import logging
import asyncio
from typing import List
import sys
import pandas as pd
import streamlit as st
import time

from config import LOG_FORMAT, LOG_FILE
from scraper import PartnerProgramScraper
from data_exporter import DataExporter
from url_processor import URLProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def process_url_batch(urls: List[str], progress_bar) -> List[dict]:
    """Process a batch of URLs using multiple threads."""
    results = []

    with PartnerProgramScraper() as scraper:
        for i, url in enumerate(urls):
            try:
                logger.info(f"Processing URL: {url}")
                result = scraper.scrape_url(url)
                results.append(result)
                # Update progress
                progress_bar.progress((i + 1) / len(urls))
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                results.append({
                    'domain': URLProcessor.get_base_domain(url),
                    'partner_program_url': '',
                    'url_path': '',
                    'program_types': [],
                    'partner_names': [],
                    'page_structure': 'unknown',
                    'status': f'error: {str(e)}'
                })

    return results

def main():
    st.title("Partner Program Scraper")
    st.write("Upload a CSV file containing URLs to scan for partner programs")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file with URLs (one per row)", type="csv")

    if uploaded_file is not None:
        try:
            # Read URLs from uploaded CSV file
            df = pd.read_csv(uploaded_file)

            # Get the first column as URLs, assuming it contains the URLs
            urls = df.iloc[:, 0].tolist()
            # Clean the URLs (remove any whitespace and empty entries)
            urls = [str(url).strip() for url in urls if str(url).strip()]

            st.write(f"Found {len(urls)} URLs to process")
            st.write("First 5 URLs to be processed:")
            st.write(urls[:5])  # Show preview of URLs

            if st.button("Start Scraping"):
                # Initialize progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Initialize data exporter
                exporter = DataExporter()

                # Process URLs
                status_text.text("Processing URLs...")
                results = process_url_batch(urls, progress_bar)

                # Export results
                exporter.export_batch(results)

                # Display results
                df_results = pd.DataFrame(results)
                st.write("Scraping Results:")
                st.dataframe(df_results)

                # Download link for CSV
                st.download_button(
                    "Download Results",
                    df_results.to_csv(index=False).encode('utf-8'),
                    "partner_programs_results.csv",
                    "text/csv",
                    key='download-csv'
                )

                status_text.text("Scraping completed!")
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")
            logger.error(f"Error processing CSV file: {str(e)}")

if __name__ == "__main__":
    main()
