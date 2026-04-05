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
import json
import os
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from models import EmailAction, EmailObservation

# --- THE FIX: GLOBAL VARIABLES TO PREVENT SERVER AMNESIA ---
GLOBAL_INDEX = 0
GLOBAL_REWARD = 0.0
GLOBAL_QUEUE = []

class MailAgentEnvironment(Environment):
    def __init__(self):
        global GLOBAL_QUEUE
        
        # Only load the JSON file once
        if not GLOBAL_QUEUE:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, "data.json")
            if not os.path.exists(data_path):
                data_path = os.path.join(os.path.dirname(current_dir), "data.json")

            try:
                with open(data_path, 'r') as f:
                    GLOBAL_QUEUE = json.load(f)
                print(f"✅ Loaded {len(GLOBAL_QUEUE)} emails")
            except Exception as e:
                print(f"❌ Failed to load: {e}")
                GLOBAL_QUEUE = []

        self._state = State(episode_id=str(uuid4()), step_count=0)

    @property
    def state(self) -> State:
        return self._state

    def reset(self) -> EmailObservation:
        """Resets the global index so you can start a fresh run."""
        global GLOBAL_INDEX, GLOBAL_REWARD
        GLOBAL_INDEX = 0
        GLOBAL_REWARD = 0.0
        self._state = State(episode_id=str(uuid4()), step_count=0)
        return self._get_current_observation(reward=0.0)

    def calculate_reward(self, true_category: str, predicted_category: str) -> float:
        true_cat = true_category.strip().lower()
        pred_cat = predicted_category.strip().lower()

        if true_cat == pred_cat:
            return 1.0
        if true_cat == "urgent" and pred_cat == "spam":
            return -2.0
        return -1.0

    def step(self, action: EmailAction) -> EmailObservation:
        global GLOBAL_INDEX, GLOBAL_REWARD, GLOBAL_QUEUE
        
        if GLOBAL_INDEX >= len(GLOBAL_QUEUE):
            return self._get_current_observation(reward=0.0)

        # 1. Score against the CURRENT global index
        current_email = GLOBAL_QUEUE[GLOBAL_INDEX]
        step_reward = self.calculate_reward(current_email["category"], action.folder)
        
        # 2. Update globals
        GLOBAL_REWARD += step_reward
        GLOBAL_INDEX += 1
        self._state.step_count += 1
        
        # 3. Return the NEXT email
        return self._get_current_observation(reward=float(step_reward))

    def _get_current_observation(self, reward: float = 0.0) -> EmailObservation:
        global GLOBAL_INDEX, GLOBAL_QUEUE
        done = GLOBAL_INDEX >= len(GLOBAL_QUEUE)
        
        if not done:
            email = GLOBAL_QUEUE[GLOBAL_INDEX]
            return EmailObservation(
                subject=email["subject"],
                email_text=email["body"],
                sender=email["sender"],
                is_vip=email.get("is_vip", False),
                reward=reward,
                done=done
            )
        
        return EmailObservation(
            subject="End",
            email_text="No more emails in inbox.",
            sender="System",
            is_vip=False,
            reward=reward,
            done=True
        )