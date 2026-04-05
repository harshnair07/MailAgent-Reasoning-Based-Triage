# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Mail Agent Environment."""

from .client import MailAgentEnv
from .models import MailAgentAction, MailAgentObservation

__all__ = [
    "MailAgentAction",
    "MailAgentObservation",
    "MailAgentEnv",
]
