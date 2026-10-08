from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Street(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class PokerState(BaseModel):
    table_size: int = Field(default=6, ge=2, le=10)
    street: Street = Street.PREFLOP
    hero_cards: List[str] = Field(default=[], description="Пример: ['As', 'Kh']")
    board: List[str] = Field(default=[], description="Пример: ['Qs', '7d', '2c']")
    total_pot_bb: float = Field(default=0.0, ge=0.0)
    effective_stack_bb: float = Field(default=100.0, ge=0.0)