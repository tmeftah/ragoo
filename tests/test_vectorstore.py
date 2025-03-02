def test_add_and_query_document(test_chroma_client):
    test_doc = "Sample document text"
    # Add non-empty metadata
    test_chroma_client.add_documents(
        documents=[test_doc], metadata=[{"source": "test"}]
    )
    results = test_chroma_client.query(test_doc)
    assert len(results) > 0
    assert test_doc in results


def test_empty_metadata_handling(test_chroma_client):
    # Test with empty metadata (if supported)
    test_doc = "Empty metadata test"
    test_chroma_client.add_documents(documents=[test_doc], metadata=[{}])
    results = test_chroma_client.query(test_doc)
    assert len(results) > 0
