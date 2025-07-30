# This is a trick to import the Page class without
# initializing the whole kvcached stack.
import sys
import unittest
from unittest.mock import MagicMock

sys.modules['kvcached.vmm_ops'] = MagicMock()
sys.modules['kvcached.tp_ipc_util'] = MagicMock()
from kvcached.kv_cache_manager import Page


class TestPageBoundary(unittest.TestCase):

    def test_page_init_non_aligned(self):
        # Test case where PAGE_SIZE is not a multiple of block_mem_size
        # Page 0: vaddr [0, 99], block_mem_size = 30
        # Block 0: [0, 29] -> in page 0
        # Block 1: [30, 59] -> in page 0
        # Block 2: [60, 89] -> in page 0
        # Block 3: [90, 119] -> spans page 0 and 1
        page = Page(page_id=0, page_size=100)
        page.init(block_mem_size=30)
        self.assertEqual(page.all_block_ids, [0, 1, 2])
        self.assertEqual(page.num_kv_blocks, 3)
        self.assertEqual(page.free_list, [0, 1, 2])

        # Page 1: vaddr [100, 199], block_mem_size = 30
        # Block 3: [90, 119] -> spans page 0 and 1
        # Block 4: [120, 149] -> in page 1
        # Block 5: [150, 179] -> in page 1
        # Block 6: [180, 209] -> spans page 1 and 2
        page = Page(page_id=1, page_size=100)
        page.init(block_mem_size=30)
        self.assertEqual(page.all_block_ids, [4, 5])
        self.assertEqual(page.num_kv_blocks, 2)
        self.assertEqual(page.free_list, [4, 5])

    def test_page_init_no_blocks(self):
        # Test case where a page contains no full blocks
        page = Page(page_id=0, page_size=100)
        page.init(block_mem_size=120)
        self.assertEqual(page.all_block_ids, [])
        self.assertEqual(page.num_kv_blocks, 0)
        self.assertEqual(page.free_list, [])

    def test_page_methods(self):
        page = Page(page_id=0, page_size=100)
        page.init(block_mem_size=30)  # all_block_ids = [0, 1, 2]

        self.assertTrue(page._has_block(0))
        self.assertTrue(page._has_block(2))
        self.assertFalse(page._has_block(3))

        self.assertEqual(page.get_used_blocks(), [])

        block_id = page.alloc()
        self.assertEqual(block_id, 2)
        self.assertEqual(page.get_used_blocks(), [2])
        self.assertEqual(page.free_list, [0, 1])

        page.free(2)
        self.assertEqual(page.get_used_blocks(), [])
        self.assertIn(2, page.free_list)


if __name__ == '__main__':
    unittest.main()
