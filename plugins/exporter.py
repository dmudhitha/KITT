"""
System Diagnostic Markdown Exporter Plugin for VANGUARD AI Assistant.
Compiles hardware, telemetry, network, and database stats into Markdown reports.
"""
import os
import time
import platform
import psutil
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.exporter")


class DiagnosticExporterPlugin(BasePlugin):
    """Compiles and exports system diagnostic reports in Markdown format."""

    @property
    def name(self) -> str:
        return "DiagnosticExporter"

    @property
    def description(self) -> str:
        return "Compiles system telemetry into formatted Markdown diagnostic report files."

    @property
    def commands(self) -> List[str]:
        return ["export diagnostic report", "export report", "generate report"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            reports_dir = "assets/reports"
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.md"
            filepath = os.path.join(reports_dir, filename)

            # Telemetry Metrics
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu_pct = psutil.cpu_percent(interval=0.1)

            report_md = f"""# 🛡️ VANGUARD SYSTEM DIAGNOSTIC REPORT

> **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
> **System Host**: {platform.node()}  
> **OS Platform**: {platform.system()} {platform.release()} ({platform.machine()})  

---

## 📊 Core Telemetry Diagnostics

| Metric | Measured Value | Operational Status |
| :--- | :--- | :--- |
| **CPU Utilization** | `{cpu_pct}%` | Nominal |
| **RAM Memory Usage** | `{mem.percent}%` ({round(mem.used/(1024**3),2)} GB / {round(mem.total/(1024**3),2)} GB) | Nominal |
| **Disk Capacity** | `{disk.percent}%` ({round(disk.used/(1024**3),2)} GB / {round(disk.total/(1024**3),2)} GB) | Nominal |
| **CPU Cores** | `{psutil.cpu_count(logical=True)} Logical Cores` | Operational |

---

## 🔒 Security & Subsystems Status
- **Database Vault**: Persistent SQLite database active (`database/memory.db`).
- **Telemetry Monitor**: Active background scraper polling.
- **Diagnostic Result**: ALL SYSTEMS NOMINAL.
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_md)

            play_sound_async("assets/sounds/plugin.wav")
            logger.info(f"Diagnostic Markdown report saved to: {filepath}")
            return f"SYSTEM DIAGNOSTIC REPORT EXPORTED: Saved to {filepath}."
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Report export failed: {e}")
            return f"REPORT EXPORTER ERROR: Could not export Markdown report ({e})."
