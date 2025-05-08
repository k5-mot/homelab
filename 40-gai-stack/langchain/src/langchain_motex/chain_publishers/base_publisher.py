#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod

# from pydantic import BaseModel


class BasePublisher(ABC):

    @abstractmethod
    def get_chain(self, model_name: str):
        pass

    @abstractmethod
    def get_chains(self):
        pass
