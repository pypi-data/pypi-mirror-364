"""
Performance benchmarking tools for rbadata.

This module provides benchmarking functionality to compare the performance
of different data fetching approaches and measure the improvements from
the enhanced rbadata package.
"""

import statistics
import time
from typing import Any, Callable, Dict, List

import pandas as pd

from .cache import get_cache
from .core import read_rba
from .csv_parser import fetch_multiple_series_csv


class RBABenchmark:
    """
    Benchmarking suite for RBA data fetching operations.

    This class provides tools to measure and compare performance across
    different data fetching methods, with support for caching, concurrency,
    and various data sources.
    """

    def __init__(self):
        """Initialize benchmark suite."""
        self.results = []
        self.cache_enabled = True

    def run_benchmark(
        self,
        test_name: str,
        test_function: Callable,
        test_args: tuple = (),
        test_kwargs: dict = None,
        iterations: int = 3,
        warmup: bool = True,
    ) -> Dict[str, Any]:
        """
        Run a single benchmark test.

        Parameters
        ----------
        test_name : str
            Name of the test
        test_function : Callable
            Function to benchmark
        test_args : tuple, default ()
            Arguments for the test function
        test_kwargs : dict, optional
            Keyword arguments for the test function
        iterations : int, default 3
            Number of iterations to run
        warmup : bool, default True
            Whether to run a warmup iteration

        Returns
        -------
        dict
            Benchmark results
        """
        if test_kwargs is None:
            test_kwargs = {}

        print(f"Running benchmark: {test_name}")

        # Warmup run
        if warmup:
            try:
                test_function(*test_args, **test_kwargs)
            except Exception as e:
                print(f"Warmup failed: {e}")

        # Actual benchmark runs
        times = []
        errors = []

        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = test_function(*test_args, **test_kwargs)
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                times.append(elapsed)

                # Verify result is valid
                if hasattr(result, "__len__"):
                    result_size = len(result)
                else:
                    result_size = 1

            except Exception as e:
                errors.append(str(e))
                end_time = time.perf_counter()
                times.append(end_time - start_time)  # Include failed attempts
                result_size = 0

        # Calculate statistics
        if times:
            benchmark_result = {
                "test_name": test_name,
                "iterations": iterations,
                "times": times,
                "min_time": min(times),
                "max_time": max(times),
                "mean_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                "total_time": sum(times),
                "errors": errors,
                "error_rate": len(errors) / iterations,
                "success_rate": (iterations - len(errors)) / iterations,
                "result_size": result_size,
            }
        else:
            benchmark_result = {
                "test_name": test_name,
                "iterations": iterations,
                "times": [],
                "min_time": float("inf"),
                "max_time": 0,
                "mean_time": float("inf"),
                "median_time": float("inf"),
                "std_dev": 0,
                "total_time": float("inf"),
                "errors": errors,
                "error_rate": 1.0,
                "success_rate": 0.0,
                "result_size": 0,
            }

        self.results.append(benchmark_result)

        print(f"  Mean time: {benchmark_result['mean_time']:.3f}s")
        print(f"  Success rate: {benchmark_result['success_rate']:.1%}")

        return benchmark_result

    def compare_csv_vs_excel(self, table_no: str = "F1") -> Dict[str, Any]:
        """
        Compare CSV vs Excel data fetching performance.

        Parameters
        ----------
        table_no : str, default 'F1'
            Table to test with

        Returns
        -------
        dict
            Comparison results
        """
        print("\n=== CSV vs Excel Performance Comparison ===")

        # Test Excel approach
        excel_result = self.run_benchmark(
            test_name=f"Excel fetch - {table_no}",
            test_function=read_rba,
            test_kwargs={"table_no": table_no, "use_csv": False, "use_cache": False},
        )

        # Test CSV approach
        csv_result = self.run_benchmark(
            test_name=f"CSV fetch - {table_no}",
            test_function=read_rba,
            test_kwargs={"table_no": table_no, "use_csv": True, "use_cache": False},
        )

        # Calculate improvement
        if excel_result["mean_time"] > 0 and csv_result["mean_time"] > 0:
            improvement = (
                excel_result["mean_time"] - csv_result["mean_time"]
            ) / excel_result["mean_time"]
            speed_ratio = excel_result["mean_time"] / csv_result["mean_time"]
        else:
            improvement = 0
            speed_ratio = 1

        comparison = {
            "excel_time": excel_result["mean_time"],
            "csv_time": csv_result["mean_time"],
            "improvement_pct": improvement * 100,
            "speed_ratio": speed_ratio,
            "csv_faster": csv_result["mean_time"] < excel_result["mean_time"],
            "excel_result": excel_result,
            "csv_result": csv_result,
        }

        print("\nResults:")
        print(f"  Excel: {excel_result['mean_time']:.3f}s")
        print(f"  CSV: {csv_result['mean_time']:.3f}s")
        print(f"  Improvement: {improvement*100:.1f}%")
        print(f"  Speed ratio: {speed_ratio:.1f}x")

        return comparison

    def benchmark_caching(self, table_no: str = "F1") -> Dict[str, Any]:
        """
        Benchmark caching performance.

        Parameters
        ----------
        table_no : str, default 'F1'
            Table to test with

        Returns
        -------
        dict
            Caching benchmark results
        """
        print("\n=== Caching Performance Benchmark ===")

        # Clear cache first
        cache = get_cache()
        cache.clear()

        # Test without cache (cold)
        no_cache_result = self.run_benchmark(
            test_name=f"No cache - {table_no}",
            test_function=read_rba,
            test_kwargs={"table_no": table_no, "use_cache": False},
            warmup=False,
        )

        # Test with cache (first call - cache miss)
        cache_miss_result = self.run_benchmark(
            test_name=f"Cache miss - {table_no}",
            test_function=read_rba,
            test_kwargs={"table_no": table_no, "use_cache": True},
            iterations=1,
            warmup=False,
        )

        # Test with cache (subsequent calls - cache hit)
        cache_hit_result = self.run_benchmark(
            test_name=f"Cache hit - {table_no}",
            test_function=read_rba,
            test_kwargs={"table_no": table_no, "use_cache": True},
            warmup=False,
        )

        # Calculate cache effectiveness
        if no_cache_result["mean_time"] > 0 and cache_hit_result["mean_time"] > 0:
            cache_speedup = no_cache_result["mean_time"] / cache_hit_result["mean_time"]
        else:
            cache_speedup = 1

        comparison = {
            "no_cache_time": no_cache_result["mean_time"],
            "cache_miss_time": cache_miss_result["mean_time"],
            "cache_hit_time": cache_hit_result["mean_time"],
            "cache_speedup": cache_speedup,
            "cache_overhead": cache_miss_result["mean_time"]
            - no_cache_result["mean_time"],
            "results": {
                "no_cache": no_cache_result,
                "cache_miss": cache_miss_result,
                "cache_hit": cache_hit_result,
            },
        }

        print("\nResults:")
        print(f"  No cache: {no_cache_result['mean_time']:.3f}s")
        print(f"  Cache miss: {cache_miss_result['mean_time']:.3f}s")
        print(f"  Cache hit: {cache_hit_result['mean_time']:.3f}s")
        print(f"  Cache speedup: {cache_speedup:.1f}x")

        return comparison

    def benchmark_bulk_fetching(self, series_ids: List[str] = None) -> Dict[str, Any]:
        """
        Benchmark bulk vs individual series fetching.

        Parameters
        ----------
        series_ids : list of str, optional
            Series to test with. Defaults to sample F1 series.

        Returns
        -------
        dict
            Bulk fetching benchmark results
        """
        if series_ids is None:
            series_ids = ["FIRMMCRTD", "FCMYGBAG2", "FCMYGBAG10"]

        print("\n=== Bulk vs Individual Fetching Benchmark ===")
        print(f"Testing with {len(series_ids)} series: {series_ids}")

        # Test individual fetching
        def fetch_individual():
            results = []
            for series_id in series_ids:
                try:
                    df = read_rba(series_id=series_id, use_cache=False)
                    results.append(df)
                except Exception:
                    pass
            return pd.concat(results, ignore_index=True) if results else pd.DataFrame()

        individual_result = self.run_benchmark(
            test_name="Individual series fetching",
            test_function=fetch_individual,
            iterations=2,  # Fewer iterations for longer tests
        )

        # Test bulk fetching
        bulk_result = self.run_benchmark(
            test_name="Bulk series fetching",
            test_function=fetch_multiple_series_csv,
            test_args=(series_ids,),
            iterations=2,
        )

        # Calculate improvement
        if individual_result["mean_time"] > 0 and bulk_result["mean_time"] > 0:
            improvement = (
                individual_result["mean_time"] - bulk_result["mean_time"]
            ) / individual_result["mean_time"]
            speed_ratio = individual_result["mean_time"] / bulk_result["mean_time"]
        else:
            improvement = 0
            speed_ratio = 1

        comparison = {
            "individual_time": individual_result["mean_time"],
            "bulk_time": bulk_result["mean_time"],
            "improvement_pct": improvement * 100,
            "speed_ratio": speed_ratio,
            "bulk_faster": bulk_result["mean_time"] < individual_result["mean_time"],
            "series_count": len(series_ids),
            "results": {"individual": individual_result, "bulk": bulk_result},
        }

        print("\nResults:")
        print(f"  Individual: {individual_result['mean_time']:.3f}s")
        print(f"  Bulk: {bulk_result['mean_time']:.3f}s")
        print(f"  Improvement: {improvement*100:.1f}%")
        print(f"  Speed ratio: {speed_ratio:.1f}x")

        return comparison

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        Run a comprehensive benchmark suite.

        Returns
        -------
        dict
            Complete benchmark results
        """
        print("🚀 Starting Comprehensive RBA Data Performance Benchmark")
        print("=" * 60)

        start_time = time.time()

        # Run all benchmarks
        csv_vs_excel = self.compare_csv_vs_excel()
        caching_perf = self.benchmark_caching()
        bulk_perf = self.benchmark_bulk_fetching()

        total_time = time.time() - start_time

        # Summary
        summary = {
            "total_benchmark_time": total_time,
            "csv_vs_excel": csv_vs_excel,
            "caching_performance": caching_perf,
            "bulk_fetching": bulk_perf,
            "overall_improvements": {
                "csv_improvement": csv_vs_excel["improvement_pct"],
                "cache_speedup": caching_perf["cache_speedup"],
                "bulk_improvement": bulk_perf["improvement_pct"],
            },
        }

        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Total benchmark time: {total_time:.1f}s")
        print("\nKey Performance Improvements:")
        print(f"  🚀 CSV vs Excel: {csv_vs_excel['improvement_pct']:.1f}% faster")
        print(f"  ⚡ Cache speedup: {caching_perf['cache_speedup']:.1f}x faster")
        print(f"  📦 Bulk fetching: {bulk_perf['improvement_pct']:.1f}% faster")

        return summary

    def export_results(self, filename: str = "rbadata_benchmark_results.json") -> None:
        """
        Export benchmark results to JSON file.

        Parameters
        ----------
        filename : str, default "rbadata_benchmark_results.json"
            Output filename
        """
        import json
        from datetime import datetime

        export_data = {
            "benchmark_timestamp": datetime.now().isoformat(),
            "rbadata_version": "2.0",  # Updated version
            "individual_results": self.results,
            "system_info": {
                "python_version": f"{pd.__version__}",  # Proxy for Python info
                "pandas_version": pd.__version__,
            },
        }

        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"✅ Benchmark results exported to {filename}")


def quick_benchmark() -> Dict[str, Any]:
    """
    Run a quick performance benchmark.

    Returns
    -------
    dict
        Quick benchmark results
    """
    print("⚡ Quick RBA Performance Benchmark")

    benchmark = RBABenchmark()

    # Just test CSV vs Excel for F1
    result = benchmark.compare_csv_vs_excel("F1")

    print("\n✅ Quick benchmark complete!")
    print(f"CSV is {result['improvement_pct']:.1f}% faster than Excel")

    return result


def comprehensive_benchmark() -> Dict[str, Any]:
    """
    Run the full comprehensive benchmark suite.

    Returns
    -------
    dict
        Complete benchmark results
    """
    benchmark = RBABenchmark()
    return benchmark.run_comprehensive_benchmark()


if __name__ == "__main__":
    # Run benchmarks when script is executed directly
    results = comprehensive_benchmark()

    # Export results
    benchmark = RBABenchmark()
    benchmark.results = results
    benchmark.export_results()
