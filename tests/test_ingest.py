import pytest
from app.src.ingest import load_pdf, chunk_text, embed_and_store, clean_text, is_already_embedded
import pathlib


def test_load_pdf_invalid_file_type(tmp_path):
    invalid_file = tmp_path / "invalid.txt"
    with pytest.raises(
        ValueError, match="Invalid file type. Please upload a valid .pdf file"
    ):
        load_pdf(invalid_file)


def test_load_valid_file():
    valid_file = pathlib.Path(__file__).parent / "data" / "sample_script.pdf"
    result = load_pdf(str(valid_file))

    assert isinstance(result, str)
    assert len(result) > 0

def test_chunk_text_normal_input():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    result = chunk_text(text)
    assert result == ["First paragraph.", "Second paragraph.", "Third paragraph."]


def test_chunk_text_empty_str():
    empty_str = ""
    result = chunk_text(empty_str)
    assert result == []


def test_chunk_text_whitespace_only():
    white_space_text = "hello\n\n \n\nworld"
    result = chunk_text(white_space_text)
    assert result == ["hello", "world"]


def test_clean_text_joins_hard_wrapped_lines():
    text = "Line one\nLine two\n\nLine three\nLine four"
    result = clean_text(text)
    assert result == "Line one Line two\n\nLine three Line four"


def test_clean_text_preserves_paragraph_breaks():
    text = "Para one.\n\nPara two.\n\nPara three."
    result = clean_text(text)
    assert result == "Para one.\n\nPara two.\n\nPara three."


def test_is_already_embedded_no_match(chroma_client):
    assert is_already_embedded(chroma_client, "abc123") is False


def test_is_already_embedded_match_found(chroma_client):
    collection = chroma_client.get_or_create_collection("scripts")
    collection.add(
        ids=["abc123_0"],
        embeddings=[[0.1, 0.2, 0.3]],
        documents=["chunk"],
        metadatas=[{"doc_hash": "abc123"}],
    )
    assert is_already_embedded(chroma_client, "abc123") is True


def test_chunk_text_splits_long_paragraph():
    # 500 words × ~5 chars each ≈ 2499 chars — forces the word-accumulation path
    long_paragraph = " ".join(["word"] * 500)
    result = chunk_text(long_paragraph, max_chars=2000)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 2000


@pytest.mark.asyncio
async def test_embed_and_store_raises_on_bad_ollama_response(mocker):
    mock_client = mocker.patch("app.src.ingest.httpx.AsyncClient")
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {"error": "context length exceeded"}
    mock_client.return_value.__aenter__.return_value.post = mocker.AsyncMock(
        return_value=mock_response
    )
    mock_chroma = mocker.MagicMock()

    with pytest.raises(RuntimeError, match="Ollama embed request failed for chunk 0"):
        await embed_and_store(
            chunks=["any chunk"],
            ollama_url="http://localhost:11434",
            chroma_client=mock_chroma,
            doc_hash="test-hash",
        )


@pytest.mark.asyncio
async def test_embed_and_store(mocker):
    mock_client = mocker.patch("app.src.ingest.httpx.AsyncClient")
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
    mock_client.return_value.__aenter__.return_value.post = mocker.AsyncMock(
        return_value=mock_response
    )
    mock_chroma = mocker.MagicMock()
    await embed_and_store(
        chunks=["chunk one", "chunk two"],
        ollama_url="http://localhost:11434",
        chroma_client=mock_chroma,
        doc_hash="test-hash",
    )

    assert mock_chroma.get_or_create_collection.return_value.add.call_count == 2
