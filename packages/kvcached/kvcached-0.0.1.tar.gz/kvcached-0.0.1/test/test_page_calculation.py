#!/usr/bin/env python3

# Mock the dependencies to avoid initializing the whole kvcached stack
import sys
import unittest
from unittest.mock import MagicMock

sys.modules['kvcached.vmm_ops'] = MagicMock()
sys.modules['kvcached.tp_ipc_util'] = MagicMock()
from kvcached.kv_cache_manager import Page, PageAllocator


class TestPageCalculation(unittest.TestCase):
    """Test page and block calculations when PAGE_SIZE is not divisible by block_mem_size."""

    def test_num_blocks_per_page_aligned(self):
        """Test when PAGE_SIZE is evenly divisible by block_mem_size."""
        allocator = PageAllocator(1000, 100, 1, False, False)  # 100-byte pages

        # 100 / 25 = 4 blocks per page (evenly divisible)
        self.assertEqual(allocator._num_blocks_per_page(25), 4)

        # 100 / 50 = 2 blocks per page (evenly divisible)
        self.assertEqual(allocator._num_blocks_per_page(50), 2)

        # 100 / 100 = 1 block per page (evenly divisible)
        self.assertEqual(allocator._num_blocks_per_page(100), 1)

    def test_num_blocks_per_page_non_aligned(self):
        """Test when PAGE_SIZE is NOT evenly divisible by block_mem_size."""
        allocator = PageAllocator(1000, 100, 1, False, False)  # 100-byte pages

        # 100 / 30 = 3.33... but only 3 complete blocks fit
        # Block 0: [0-29], Block 1: [30-59], Block 2: [60-89], Block 3: [90-119] (spans boundary)
        self.assertEqual(allocator._num_blocks_per_page(30), 3)

        # 100 / 40 = 2.5 but only 2 complete blocks fit
        # Block 0: [0-39], Block 1: [40-79], Block 2: [80-119] (spans boundary)
        self.assertEqual(allocator._num_blocks_per_page(40), 2)

        # 100 / 60 = 1.66... but only 1 complete block fits
        # Block 0: [0-59], Block 1: [60-119] (spans boundary)
        self.assertEqual(allocator._num_blocks_per_page(60), 1)

        # 100 / 120 = 0.83... no complete blocks fit
        # Block 0: [0-119] (spans boundary)
        self.assertEqual(allocator._num_blocks_per_page(120), 0)

    def test_page_init_consistency(self):
        """Test that Page.init() results are consistent with _num_blocks_per_page."""
        page_size = 100

        test_cases = [25, 30, 40, 50, 60, 100, 120]

        for block_mem_size in test_cases:
            with self.subTest(block_mem_size=block_mem_size):
                # Create a page and initialize it
                page = Page(page_id=0, page_size=page_size)
                page.init(block_mem_size)

                # Create allocator and check _num_blocks_per_page
                allocator = PageAllocator(1000, page_size, 1, False, False)
                expected_blocks = allocator._num_blocks_per_page(
                    block_mem_size)

                # They should match
                self.assertEqual(
                    page.num_kv_blocks, expected_blocks,
                    f"Page.init() found {page.num_kv_blocks} blocks but "
                    f"_num_blocks_per_page() calculated {expected_blocks} for block_mem_size={block_mem_size}"
                )

    def test_get_num_blocks_methods(self):
        """Test that get_num_*_blocks methods work correctly with non-aligned block sizes."""
        total_mem = 1000
        page_size = 100
        allocator = PageAllocator(total_mem, page_size, 1, False, False)

        # 10 pages total
        total_pages = 10
        self.assertEqual(allocator.get_num_total_pages(), total_pages)

        # Test with non-aligned block size
        block_mem_size = 30  # 3 blocks per page
        blocks_per_page = 3

        expected_total_blocks = total_pages * blocks_per_page
        self.assertEqual(allocator.get_num_total_blocks(block_mem_size),
                         expected_total_blocks)
        self.assertEqual(allocator.get_num_free_blocks(block_mem_size),
                         expected_total_blocks)
        self.assertEqual(allocator.get_num_inuse_blocks(block_mem_size), 0)

    def test_edge_cases(self):
        """Test edge cases."""
        allocator = PageAllocator(1000, 100, 1, False, False)

        # Block size equals page size
        self.assertEqual(allocator._num_blocks_per_page(100), 1)

        # Block size larger than page size
        self.assertEqual(allocator._num_blocks_per_page(150), 0)

        # Very small block size
        self.assertEqual(allocator._num_blocks_per_page(1), 100)

        # Zero or negative block size (should handle gracefully)
        self.assertEqual(allocator._num_blocks_per_page(0), 0)

    def test_specific_example(self):
        """Test the specific example from the problem description."""
        # Create a scenario where blocks span page boundaries
        page_size = 100
        block_mem_size = 30

        # Test Page 0: should contain blocks [0, 1, 2]
        page0 = Page(page_id=0, page_size=page_size)
        page0.init(block_mem_size)
        self.assertEqual(page0.all_block_ids, [0, 1, 2])

        # Test Page 1: should contain blocks [4, 5] (block 3 spans pages 0-1)
        page1 = Page(page_id=1, page_size=page_size)
        page1.init(block_mem_size)
        self.assertEqual(page1.all_block_ids, [4, 5])

        # Test Page 2: should contain blocks [7, 8, 9] (block 6 spans pages 1-2)
        page2 = Page(page_id=2, page_size=page_size)
        page2.init(block_mem_size)
        self.assertEqual(page2.all_block_ids, [7, 8, 9])


if __name__ == '__main__':
    unittest.main()
