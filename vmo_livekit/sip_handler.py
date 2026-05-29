"""SIP header extraction → session context.

LiveKit SIP receives headers from the INVITE. We extract them into a
structured session context that gets attached to every log and trace.
"""

import uuid
from dataclasses import dataclass, field


@dataclass
class SessionContext:
    """Immutable session data extracted from SIP headers."""
    vmo_call_id: str
    channel_id: str = ""
    tenant_id: str = ""
    tenant_name: str = ""
    did: str = ""
    caller_id: str = ""
    call_id_sbc: str = ""

    @classmethod
    def from_sip_headers(cls, headers: dict[str, str]) -> "SessionContext":
        """Extract session context from LiveKit SIP participant attributes.

        Headers expected (custom X- headers from SBC):
          X-VMO-Call-ID, X-Tenant-ID, X-Tenant-Name, X-DID, X-Caller-ID,
          X-SBC-Call-ID
        """
        return cls(
            vmo_call_id=headers.get("X-VMO-Call-ID", str(uuid.uuid4())),
            channel_id=headers.get("X-Channel-ID", ""),
            tenant_id=headers.get("X-Tenant-ID", "default"),
            tenant_name=headers.get("X-Tenant-Name", "Default"),
            did=headers.get("X-DID", ""),
            caller_id=headers.get("X-Caller-ID", ""),
            call_id_sbc=headers.get("X-SBC-Call-ID", ""),
        )

    def asdict(self) -> dict:
        return {
            "vmo_call_id": self.vmo_call_id,
            "channel_id": self.channel_id,
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "did": self.did,
            "caller_id": self.caller_id,
            "call_id_sbc": self.call_id_sbc,
        }
