import pytest
from app.src.ingest import load_pdf, chunk_text, embed_and_store
import pathlib

def test_load_pdf_invalid_file_type(tmp_path):
    invalid_file = tmp_path/ "invalid.txt"
    with pytest.raises(ValueError, match="Invalid file type. Please upload a valid .pdf file"):
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

@pytest.mark.asyncio
async def test_embed_and_store(mocker):
    mock_client = mocker.patch("app.src.ingest.httpx.AsyncClient")
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
    mock_client.return_value.__aenter__.return_value.post = mocker.AsyncMock(return_value=mock_response)
    mock_chroma = mocker.MagicMock()
    result = await embed_and_store(chunks=["chunk one", "chunk two"], ollama_url="http://localhost:11434", chroma_client=mock_chroma)

    assert mock_chroma.get_or_create_collection.return_value.add.call_count == 2

