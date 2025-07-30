from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from ide.core.logger import ide_logger as logger
from ide.events.async_event_store_wrapper import AsyncEventStoreWrapper
from ide.events.event_filter import EventFilter
from ide.events.serialization import event_to_trajectory
from ide.server.dependencies import get_dependencies
from ide.server.session.conversation import ServerConversation
from ide.server.utils import get_conversation

app = APIRouter(
    prefix='/api/conversations/{conversation_id}', dependencies=get_dependencies()
)


@app.get('/trajectory')
async def get_trajectory(
    conversation: ServerConversation = Depends(get_conversation),
) -> JSONResponse:
    """Get trajectory.

    This function retrieves the current trajectory and returns it.

    Args:
        request (Request): The incoming request object.

    Returns:
        JSONResponse: A JSON response containing the trajectory as a list of
        events.
    """
    try:
        async_store = AsyncEventStoreWrapper(
            conversation.event_stream, filter=EventFilter(exclude_hidden=True)
        )
        trajectory = []
        async for event in async_store:
            trajectory.append(event_to_trajectory(event))
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={'trajectory': trajectory}
        )
    except Exception as e:
        logger.error(f'Error getting trajectory: {e}', exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'trajectory': None,
                'error': f'Error getting trajectory: {e}',
            },
        )
