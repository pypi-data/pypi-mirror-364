from __future__ import annotations

import unittest
from weakref import ref

from weaktree.node import (
    CleanupMode,
    WeakTreeNode,
    ItemsIterable,
    NodeIterable,
    ValueIterable,
)


class TestObject:

    def __init__(self, data):
        self.data = data

    def __repr__(self) -> str:
        return f"TestObject({str(self.data)})"


class TestNode(unittest.TestCase):

    def setUp(self) -> None:
        test_data: dict[str, TestObject] = {
            "root": TestObject("Root"),
            "1": TestObject("1"),
            "2": TestObject("2"),
            "3": TestObject("3"),
            "4": TestObject("4"),
            "5": TestObject("5"),
            "6": TestObject("6"),
            "7": TestObject("7"),
            "8": TestObject("8"),
            "9": TestObject("9"),
        }
        self.test_data = test_data

        self.root = WeakTreeNode(test_data["root"])

        branch1 = self.root.add_branch(test_data["1"])

        branch4 = branch1.add_branch(test_data["4"])
        branch8 = branch4.add_branch(test_data["8"])
        branch8.add_branch(test_data["9"])

        branch1.add_branch(test_data["5"])

        branch2 = self.root.add_branch(test_data["2"])
        branch2.add_branch(test_data["6"])

        branch3 = self.root.add_branch(test_data["3"])
        branch3.add_branch(test_data["7"])

        # Note: These excess vars all descope after setup, so we don't have to worry
        # about excess references.
        # We could also do this by chaining add_branch, but that actually becomes
        # _less_ readable.

    def test_nodes(self):
        self.assertIsInstance(self.root.nodes(), NodeIterable)

    def test_values(self):
        self.assertIsInstance(self.root.values(), ValueIterable)

    def test_items(self):
        self.assertIsInstance(self.root.items(), ItemsIterable)

    def test_callback(self):
        # Add a custom callback to a node that will get cleaned up.

        global callback_ran
        callback_ran = False

        def callback(wr):
            global callback_ran
            callback_ran = True

        ephemeral_data = TestObject("NotLongForThisWorld")

        WeakTreeNode(ephemeral_data, self.root, callback=callback)

        del ephemeral_data

        self.assertTrue(callback_ran)

    def setup_ephemeral_data(
        self,
        cleanup_mode: CleanupMode = WeakTreeNode.DEFAULT,
    ) -> tuple[dict[str, TestObject], ref[WeakTreeNode], ref[WeakTreeNode]]:
        ephemeral_data = {
            "1": TestObject("E1"),
            "2": TestObject("E2"),
            "3": TestObject("E3"),
        }

        branch_e1 = WeakTreeNode(ephemeral_data["1"], self.root, cleanup_mode)
        branch_e2 = branch_e1.add_branch(ephemeral_data["2"])
        branch_e3_wr = ref(branch_e2.add_branch(ephemeral_data["3"]))

        branch_e2_wr = ref(branch_e2)

        return ephemeral_data, branch_e2_wr, branch_e3_wr

    def test_prune(self):

        ephemeral_data, branch_e2_wr, branch_e3_wr = self.setup_ephemeral_data()

        # Ensure our nodes exist
        self.assertIsNotNone(branch_e2_wr())
        self.assertIsNotNone(branch_e3_wr())

        ephemeral_data.pop("1")

        # This should cause branch_e1 to dissolve, and unwind branch_e2
        self.assertIsNone(branch_e2_wr())
        self.assertIsNone(branch_e3_wr())

    def test_reparent(self):

        ephemeral_data, branch_e2_wr, branch_e3_wr = self.setup_ephemeral_data(
            WeakTreeNode.REPARENT
        )

        # Ensure our nodes exist
        self.assertIsNotNone(branch_e2_wr())
        self.assertIsNotNone(branch_e3_wr())

        ephemeral_data.pop("1")

        # We want our nodes to still exist
        branch_e2 = branch_e2_wr()
        self.assertIsNotNone(branch_e2)
        self.assertIsNotNone(branch_e3_wr())

        assert branch_e2  # for the static type checker

        # e2 should now be a child of self.root
        self.assertIs(branch_e2.trunk, self.root)

    def test_no_cleanup(self):

        ephemeral_data, branch_e2_wr, branch_e3_wr = self.setup_ephemeral_data(
            WeakTreeNode.NO_CLEANUP
        )

        # Ensure our nodes exist
        self.assertIsNotNone(branch_e2_wr())
        self.assertIsNotNone(branch_e3_wr())

        ephemeral_data.pop("1")

        # We want our nodes to still exist
        branch_e2 = branch_e2_wr()
        self.assertIsNotNone(branch_e2)
        self.assertIsNotNone(branch_e3_wr())

        assert branch_e2  # for the static type checker

        # e1 should still exist and still be the parent of e2
        branch_e1 = branch_e2.trunk
        self.assertIsNotNone(branch_e1)
        assert isinstance(branch_e1, WeakTreeNode)
        # e1 should be empty, or rather the weakref should return None
        self.assertIsNone(branch_e1.data)

    def test_data_setter(self):

        _, branch_e2_wr, branch_e3_wr = self.setup_ephemeral_data()

        replacement_data = TestObject("Replaced")

        branch_e2 = branch_e2_wr()
        assert branch_e2  # for the static type checker

        branch_e1 = branch_e2.trunk
        assert branch_e1

        del branch_e2

        branch_e1.data = replacement_data

        self.assertIsNotNone(branch_e1.data)

        del replacement_data

        # Ensure the data has expired
        self.assertIsNone(branch_e1.data)

        # Ensure our branches have dissolved
        self.assertIsNone(branch_e2_wr())
        self.assertIsNone(branch_e3_wr())


if __name__ == "__main__":
    unittest.main()
