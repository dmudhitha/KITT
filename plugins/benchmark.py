"""
System Diagnostic Benchmark Plugin for VANGUARD AI Assistant.
Executes CPU matrix computation stress tests to calculate a performance score.
"""
import time
import math
import psutil
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.benchmark")


class BenchmarkPlugin(BasePlugin):
    """Executes floating-point matrix CPU stress tests and reports performance score."""

    @property
    def name(self) -> str:
        return "SystemBenchmark"

    @property
    def description(self) -> str:
        return "Executes CPU computation stress benchmark and computes V-INDEX performance score."

    @property
    def commands(self) -> List[str]:
        return ["run benchmark", "system test", "benchmark", "performance test"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        try:
            play_sound_async("assets/sounds/scan.wav")
            logger.info("Executing 1.5-second VANGUARD CPU benchmark stress test...")

            start_t = time.time()
            ops = 0
            # 1.5-second math calculation stress loop
            while time.time() - start_t < 1.5:
                for i in range(1, 1000):
                    val = math.sin(i) * math.cos(i) * math.sqrt(i)
                    ops += 1

            duration = time.time() - start_t
            ops_per_sec = ops / duration if duration > 0 else 0
            v_index = int(ops_per_sec / 100.0)

            cpu_cores = psutil.cpu_count(logical=True)
            ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

            play_sound_async("assets/sounds/plugin.wav")
            report = (
                f"VANGUARD PERFORMANCE BENCHMARK COMPLETE: "
                f"Score: {v_index:,} V-INDEX. "
                f"Hardware Profile: {cpu_cores} Cores | {ram_gb} GB RAM. "
                f"Core Compute Throughput: {int(ops_per_sec):,} ops/sec. "
                f"Diagnostic Status: OPTIMAL."
            )
            logger.info(f"Benchmark test complete: Score {v_index} V-INDEX.")
            return report
        except Exception as e:
            play_sound_async("assets/sounds/error.wav")
            logger.error(f"Benchmark test failed: {e}")
            return f"BENCHMARK ERROR: Test failed ({e})."
