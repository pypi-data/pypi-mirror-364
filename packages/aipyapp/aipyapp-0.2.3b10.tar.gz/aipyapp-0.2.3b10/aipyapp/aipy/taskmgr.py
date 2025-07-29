#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from collections import deque, namedtuple

from loguru import logger

from .. import T
from .task import Task
from .plugin import PluginManager
from .prompt import get_system_prompt
from .diagnose import Diagnose
from .llm import ClientManager
from .config import PLUGINS_DIR, TIPS_DIR, get_mcp_config_file, get_tt_api_key
from .tips import TipsManager
from .mcp_tool import MCPToolManager

class TaskManager:
    MAX_TASKS = 16

    def __init__(self, settings, console, gui=False):
        self.settings = settings
        self.console = console
        self.tasks = deque(maxlen=self.MAX_TASKS)
        self.envs = {}
        self.gui = gui
        self.log = logger.bind(src='taskmgr')
        self.api_prompt = None
        self.config_files = settings._loaded_files
        self.plugin_manager = PluginManager(PLUGINS_DIR)
        self.plugin_manager.load_plugins()
        if settings.workdir:
            workdir = Path.cwd() / settings.workdir
            workdir.mkdir(parents=True, exist_ok=True)
            os.chdir(workdir)
            self.cwd = workdir
        else:
            self.cwd = Path.cwd()
        self._init_environ()
        self.tt_api_key = get_tt_api_key(settings)
        # 始终初始化MCPToolManager，内置工具也需要它
        mcp_config_file = get_mcp_config_file(settings.get('_config_dir'))
        self.mcp = MCPToolManager(mcp_config_file, self.tt_api_key)
        self._init_api()
        self.diagnose = Diagnose.create(settings)
        self.client_manager = ClientManager(settings)
        self.tips_manager = TipsManager(TIPS_DIR)
        self.tips_manager.load_tips()
        self.tips_manager.use(settings.get('role', 'aipy'))
        self.task = None

    @property
    def workdir(self):
        return str(self.cwd)

    def get_tasks(self):
        return list(self.tasks)

    def list_llms(self):
        return self.client_manager.to_records()
    
    def list_envs(self):
        EnvRecord = namedtuple('EnvRecord', ['Name', 'Description', 'Value'])
        rows = []
        for name, (value, desc) in self.envs.items():    
            rows.append(EnvRecord(name, desc, value[:32]))
        return rows
    
    def list_tasks(self):
        rows = []
        for task in self.tasks:
            rows.append(task.to_record())
        return rows
    
    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_update(self, force=False):
        return self.diagnose.check_update(force)

    def use(self, llm=None, role=None, task=None):
        if llm:
            ret = self.client_manager.use(llm)
            self.console.print(f"LLM: {'[green]Ok[/green]' if ret else '[red]Error[/red]'}")
        if role:
            ret = self.tips_manager.use(role)
            self.console.print(f"Role: {'[green]Ok[/green]' if ret else '[red]Error[/red]'}")
        if task:
            task = self.get_task_by_id(task)
            self.console.print(f"Task: {'[green]Ok[/green]' if task else '[red]Error[/red]'}")
            self.task = task

    def _init_environ(self):
        envs = self.settings.get('environ', {})
        for name, value in envs.items():
            os.environ[name] = value

    def _init_api(self):
        api = self.settings.get('api', {})

        lines = []
        for api_name, api_conf in api.items():
            lines.append(f"## {api_name} API")
            desc = api_conf.get('desc')
            if desc:
                lines.append(f"### API {T('Description')}\n{desc}")

            envs = api_conf.get('env')
            if not envs:
                continue

            lines.append(f"### {T('Environment variable name and meaning')}")
            for name, (value, desc) in envs.items():
                value = value.strip()
                if not value:
                    continue
                lines.append(f"- {name}: {desc}")
                self.envs[name] = (value, desc)

        self.api_prompt = "\n".join(lines)

    def new_task(self):
        if self.task:
            task = self.task
            self.task = None
            self.log.info('Reload task', task_id=task.task_id)
            return task

        with_mcp = self.settings.get('mcp', {}).get('enable', True)

        mcp_tools = ""
        if self.mcp and with_mcp:
            mcp_tools = self.mcp.get_tools_prompt()
        system_prompt = get_system_prompt(
            self.tips_manager.current_tips,
            self.api_prompt,
            self.settings.get('system_prompt'),
            mcp_tools=mcp_tools
        )

        task = Task(self)
        task.client = self.client_manager.Client()
        task.diagnose = self.diagnose
        task.system_prompt = system_prompt
        task.mcp = self.mcp if with_mcp else None
        self.tasks.append(task)
        self.log.info('New task created', task_id=task.task_id)
        return task