from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ..value_objects.inventory_value_objects import ReapproStatus


@dataclass
class CreateReapproRequest:
    store_id: int
    product_id: int
    quantity: int
    notes: Optional[str] = None


@dataclass
class UpdateReapproRequest:
    request_id: int
    quantity: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class ProcessReapproRequest:
    request_id: int
    action: str  # "approve" or "reject"
    notes: Optional[str] = None


@dataclass
class ReapproRequestResponse:
    id: int
    store_id: int
    product_id: int
    quantity: int
    status: str
    requested_at: str
    processed_at: Optional[str]
    notes: Optional[str]
    store_name: Optional[str]
    product_name: Optional[str]


@dataclass
class ReapproRequestListResponse:
    requests: List[ReapproRequestResponse]
    total: int
    page: int
    per_page: int


@dataclass
class ReapproStatsResponse:
    total_requests: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    completed_requests: int
    requests_by_store: Dict[int, int]
    requests_by_product: Dict[int, int]
