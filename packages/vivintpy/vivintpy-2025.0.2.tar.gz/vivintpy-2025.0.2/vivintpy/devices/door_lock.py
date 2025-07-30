"""Module that implements the DoorLock class."""

from __future__ import annotations

from typing import cast

from ..const import LockAttribute
from ..const import ZWaveDeviceAttribute as Attribute
from . import BypassTamperDevice


class DoorLock(BypassTamperDevice):
    """Represents a vivint door lock device."""

    @property
    def is_locked(self) -> bool:
        """Return True if door lock is locked."""
        return bool(self.data[Attribute.STATE])

    @property
    def is_online(self) -> bool:
        """Return True if door lock is online."""
        return bool(self.data[Attribute.ONLINE])

    @property
    def user_code_list(self) -> list[int]:
        """Return the user code list."""
        return cast(list[int], self.data.get(LockAttribute.USER_CODE_LIST, []))

    async def set_state(self, locked: bool) -> None:
        """Set door lock's state."""
        assert self.alarm_panel
        await self.api.set_lock_state(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, locked
        )

    async def lock(self) -> None:
        """Lock the door lock."""
        await self.set_state(True)

    async def unlock(self) -> None:
        """Unlock the door lock."""
        await self.set_state(False)
