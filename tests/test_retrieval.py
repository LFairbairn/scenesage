import pytest
from app.src.retrieval import retrieve_chunks, generate_answer


@pytest.mark.asyncio
async def test_retrieve_chunks(mocker, chroma_client):
    collection = chroma_client.get_or_create_collection("scripts")
    collection.add(
        ids=["1"],
        embeddings=[[0.1, 0.2, 0.3]],
        documents=["A test chunk of script text"],
    )
    mock_client = mocker.patch("app.src.retrieval.httpx.AsyncClient")
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
    mock_client.return_value.__aenter__.return_value.post = mocker.AsyncMock(
        return_value=mock_response
    )

    results = await retrieve_chunks(
        "test query", ollama_url="http://localhost:11434", chroma_client=chroma_client
    )

    assert results[0] == "A test chunk of script text"


@pytest.mark.asyncio
async def test_generate_answer(mocker):
    mock_client = mocker.patch("app.src.retrieval.httpx.AsyncClient")
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {"response": "some answer text"}
    mock_client.return_value.__aenter__.return_value.post = mocker.AsyncMock(
        return_value=mock_response
    )

    results = await generate_answer(
        chunks=["A test chunk of script text"],
        query="What happens in the first scene?",
        ollama_url="http://localhost:11434",
    )

    assert results == "some answer text"
