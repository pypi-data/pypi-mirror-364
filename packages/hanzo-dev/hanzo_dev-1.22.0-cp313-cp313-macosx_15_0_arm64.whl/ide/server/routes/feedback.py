from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from ide.core.logger import ide_logger as logger
from ide.events.async_event_store_wrapper import AsyncEventStoreWrapper
from ide.events.event_filter import EventFilter
from ide.events.serialization import event_to_dict
from ide.server.data_models.feedback import FeedbackDataModel, store_feedback
from ide.server.dependencies import get_dependencies
from ide.server.session.conversation import ServerConversation
from ide.server.utils import get_conversation
from ide.utils.async_utils import call_sync_from_async

app = APIRouter(
    prefix='/api/conversations/{conversation_id}', dependencies=get_dependencies()
)


@app.post('/submit-feedback')
async def submit_feedback(
    request: Request, conversation: ServerConversation = Depends(get_conversation)
) -> JSONResponse:
    """Submit user feedback.

    This function stores the provided feedback data.

    To submit feedback:
    ```sh
    curl -X POST -d '{"email": "test@example.com"}' -H "Authorization:"
    ```

    Args:
        request (Request): The incoming request object.
        feedback (FeedbackDataModel): The feedback data to be stored.

    Returns:
        dict: The stored feedback data.

    Raises:
        HTTPException: If there's an error submitting the feedback.
    """
    # Assuming the storage service is already configured in the backend
    # and there is a function to handle the storage.
    body = await request.json()
    async_store = AsyncEventStoreWrapper(
        conversation.event_stream, filter=EventFilter(exclude_hidden=True)
    )
    trajectory = []
    async for event in async_store:
        trajectory.append(event_to_dict(event))
    feedback = FeedbackDataModel(
        email=body.get('email', ''),
        version=body.get('version', ''),
        permissions=body.get('permissions', 'private'),
        polarity=body.get('polarity', ''),
        feedback=body.get('polarity', ''),
        trajectory=trajectory,
    )
    try:
        feedback_data = await call_sync_from_async(store_feedback, feedback)
        return JSONResponse(status_code=status.HTTP_200_OK, content=feedback_data)
    except Exception as e:
        logger.error(f'Error submitting feedback: {e}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'error': 'Failed to submit feedback'},
        )
