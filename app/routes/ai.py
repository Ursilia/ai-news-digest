from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas import SummarizeRequest, SummarizeResponse, AskRequest, AskResponse
from app import services, models

from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    request: SummarizeRequest,
    current_user: models.User = Depends(get_current_user),
):
    summary = await services.summarize_article(text=request.text)
    return SummarizeResponse(summary=summary)


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    current_user: models.User = Depends(get_current_user)
):
    answer = await services.ask_question(
        question=request.question,
        history=request.history,
    )
    return AskResponse(answer=answer)


@router.post("/ask/stream")
async def ask_stream(
    request: AskRequest,
    current_user: models.User = Depends(get_current_user),
):
    async def event_generator():
        async for chunk in services.ask_question_stream(
            question=request.question,
            history=request.history,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )

