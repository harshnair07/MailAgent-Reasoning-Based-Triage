# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Mail Agent Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""

from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State


try:
    from .models import EmailAction, EmailObservation
except ImportError:
    from models import EmailAction, EmailObservation

class MailAgentEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)

    def reset(self) -> EmailObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        return EmailObservation(
            email_text="System Initialized. Awaiting Emails...",
            sender="system@mailagent.ai",
            is_vip=False
        )

    def step(self, action: EmailAction) -> EmailObservation:
        self._state.step_count += 1
        return EmailObservation(
            email_text=f"Agent moved email to {action.folder} because: {action.reasoning}",
            sender="agent@mailagent.ai",
            is_vip=False
        )

    @property
    def state(self) -> State:
        return self._state