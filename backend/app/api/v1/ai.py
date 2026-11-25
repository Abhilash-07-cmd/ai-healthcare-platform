from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.ai import (
    ChatConversationCreate,
    ChatConversationResponse,
    ChatConversationListItem,
    ChatRequest,
    ChatResponse
)
from app.services.ai_service import (
    create_conversation,
    get_patient_conversations,
    get_conversation_messages,
    process_chat_message
)
from app.api.deps import RequireRole
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/ai", tags=["AI Care Navigator"])


@router.post(
    "/conversations",
    response_model=ChatConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start New AI Care Navigation Session",
    description="Creates a new conversation session for AI-powered administrative care navigation."
)
def start_conversation(
    conv_in: ChatConversationCreate,
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    return create_conversation(db=db, patient_user_id=current_user.id, conv_in=conv_in)


@router.get(
    "/conversations",
    response_model=List[ChatConversationResponse],
    summary="List Patient Conversation Sessions",
    description="Returns all AI care navigation session history for the logged-in patient."
)
def list_conversations(
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    return get_patient_conversations(db=db, patient_user_id=current_user.id)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ChatConversationResponse,
    summary="Get Conversation with Full Message History",
    description="Retrieves a specific conversation session including all persisted messages."
)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    return get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        patient_user_id=current_user.id
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send Message to AI Care Navigator",
    description=(
        "Sends a message to the AI Care Navigator and receives an administrative response "
        "with department matching, doctor recommendations, and safety guardrails. "
        "Medical diagnostic queries automatically trigger safety disclaimers."
    )
)
def chat_with_ai(
    chat_in: ChatRequest,
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    return process_chat_message(db=db, patient_user_id=current_user.id, chat_in=chat_in)
