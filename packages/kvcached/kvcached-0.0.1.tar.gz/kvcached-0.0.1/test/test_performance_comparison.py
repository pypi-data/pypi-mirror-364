#!/usr/bin/env python3

# Mock dependencies
import sys
import time
import unittest
from unittest.mock import MagicMock

sys.modules['kvcached.vmm_ops'] = MagicMock()
sys.modules['kvcached.tp_ipc_util'] = MagicMock()
from kvcached.kv_cache_manager import Page, PageAllocator


class TestPerformanceComparison(unittest.TestCase):
    """Compare performance of optimized vs iterative implementation."""

    def test_page_init_performance(self):
        """Test Page.init() performance with various scenarios."""
        test_cases = [
            (100, 30),  # Non-aligned case
            (1024, 64),  # Aligned case
            (2048, 100),  # Another non-aligned case
            (4096, 512),  # Large aligned case
        ]

        num_iterations = 1000

        for page_size, block_mem_size in test_cases:
            with self.subTest(page_size=page_size,
                              block_mem_size=block_mem_size):

                # Test current optimized implementation
                start_time = time.time()
                for i in range(num_iterations):
                    page = Page(page_id=i % 10, page_size=page_size)
                    page.init(block_mem_size)
                optimized_time = time.time() - start_time

                print(f"Page size: {page_size}, Block size: {block_mem_size}")
                print(
                    f"Optimized implementation: {optimized_time:.4f}s for {num_iterations} iterations"
                )
                print(
                    f"Average per operation: {optimized_time/num_iterations*1000:.3f}ms"
                )
                print()

    def test_num_blocks_per_page_performance(self):
        """Test _num_blocks_per_page performance."""
        test_cases = [
            (100, 30),  # Non-aligned case
            (1024, 64),  # Aligned case  
            (2048, 100),  # Another non-aligned case
            (4096, 512),  # Large aligned case
            (8192, 1000),  # Very non-aligned case
        ]

        num_iterations = 10000

        for page_size, block_mem_size in test_cases:
            with self.subTest(page_size=page_size,
                              block_mem_size=block_mem_size):
                allocator = PageAllocator(10000, page_size, 1, False, False)

                # Test current optimized implementation
                start_time = time.time()
                for _ in range(num_iterations):
                    result = allocator._num_blocks_per_page(block_mem_size)
                optimized_time = time.time() - start_time

                print(
                    f"Page size: {page_size}, Block size: {block_mem_size}, Blocks per page: {result}"
                )
                print(
                    f"Optimized implementation: {optimized_time:.4f}s for {num_iterations} iterations"
                )
                print(
                    f"Average per operation: {optimized_time/num_iterations*1000000:.3f}μs"
                )
                print()

    def test_correctness_edge_cases(self):
        """Test correctness with various edge cases."""
        edge_cases = [
            (100, 100),  # Block size equals page size
            (100, 200),  # Block size larger than page size
            (100, 1),  # Very small blocks
            (100, 33),  # Prime number block size
            (1024, 333),  # Another prime number case
        ]

        for page_size, block_mem_size in edge_cases:
            with self.subTest(page_size=page_size,
                              block_mem_size=block_mem_size):
                # Test Page.init()
                page = Page(page_id=0, page_size=page_size)
                page.init(block_mem_size)

                # Test PageAllocator._num_blocks_per_page()
                allocator = PageAllocator(10000, page_size, 1, False, False)
                calculated_blocks = allocator._num_blocks_per_page(
                    block_mem_size)

                # They should match
                self.assertEqual(
                    page.num_kv_blocks, calculated_blocks,
                    f"Mismatch for page_size={page_size}, block_mem_size={block_mem_size}: "
                    f"Page.init() found {page.num_kv_blocks} blocks but "
                    f"_num_blocks_per_page() calculated {calculated_blocks}")

                print(
                    f"✓ Page size: {page_size}, Block size: {block_mem_size}, Blocks: {calculated_blocks}"
                )


if __name__ == '__main__':
    # Run performance tests first
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestPerformanceComparison)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
