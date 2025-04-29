"""
AutoGPT - نظام وكلاء الذكاء الاصطناعي المستقلين
=======================================
نظام يسمح بإنشاء وإدارة وكلاء ذكاء اصطناعي يمكنهم تنفيذ المهام بشكل مستقل.
"""

__version__ = "0.1.0"
__author__ = "AutoGPT Team"
__email__ = "info@autogpt.example.com"

from core import AutoGPT, Agent, Task, TaskStatus

__all__ = ['AutoGPT', 'Agent', 'Task', 'TaskStatus']