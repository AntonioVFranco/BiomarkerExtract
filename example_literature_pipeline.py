"""Example usage of BiomarkerExtract literature pipeline."""

from langextract.literature import batch_processor

def main():
    processor = batch_processor.LiteratureBatchProcessor(
        pubmed_email="your.email@domain.com",
        pubmed_api_key="YOUR_API_KEY",
        max_workers=5
    )
    
    biomarker_terms = [
        "DNA methylation clock",
        "Horvath clock",
        "epigenetic age",
        "GDF-15"
    ]
    
    print("Searching for biomarker papers...")
    result = processor.search_biomarkers_comprehensive(
        biomarker_terms=biomarker_terms,
        max_pubmed_results=10,
        preprint_days_back=30
    )
    
    print(f"\nResults:")
    print(f"Total papers found: {result.successful}")
    print(f"Processing time: {result.processing_time_seconds:.2f}s")
    print(f"Success rate: {result.success_rate():.1f}%")
    
    print(f"\nFirst 3 papers:")
    for i, paper in enumerate(result.papers[:3], 1):
        print(f"\n{i}. {paper.metadata.title}")
        print(f"   Authors: {len(paper.metadata.authors)} authors")
        print(f"   Source: {paper.metadata.source}")
        if paper.metadata.doi:
            print(f"   DOI: {paper.metadata.doi}")

if __name__ == "__main__":
    main()
