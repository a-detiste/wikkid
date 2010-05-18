#
# Copyright (C) 2010 Wikkid Developers.
#
# This software is licensed under the GNU Affero General Public License
# version 3 (see the file LICENSE).

"""Tests for the wikkid.filestore.bzr.FileStore."""

from textwrap import dedent

from bzrlib.tests import TestCaseWithTransport

from wikkid.errors import UpdateConflicts
from wikkid.filestore.bzr import FileStore
from wikkid.tests import ProvidesMixin
from wikkid.tests.filestore import TestFileStore


class TestBzrFileStore(TestCaseWithTransport, ProvidesMixin, TestFileStore):
    """Tests for the bzr filestore and files."""

    def make_filestore(self, contents=None):
        tree = self.make_branch_and_tree('.')
        if contents:
            self.build_tree_contents(contents)
        tree.smart_add(['.'])
        tree.commit(message='Initial commit', authors=['test@example.com'])
        return FileStore(tree)

    def test_conflicts(self):
        filestore = self.make_filestore(
            [('test.txt', 'one line of content\n')])
        f = filestore.get_file('test.txt')
        base_rev = f.last_modified_in_revision
        # First update succeeds.
        filestore.update_file(
            'test.txt',
            'different line\n',
            'Test Author <test@example.com>',
            base_rev)
        # Second update with same base revision should raise an exception.
        conflicts = self.assertRaises(
            UpdateConflicts,
            filestore.update_file,
            'test.txt',
            'also change the first line\n',
            'Test Author <test@example.com>',
            base_rev)
        curr = filestore.get_file('test.txt')
        self.assertEqual(
            curr.last_modified_in_revision,
            conflicts.basis_rev)
        self.assertEqual(dedent("""\
            <<<<<<<
            also change the first line
            =======
            different line
            >>>>>>>
            """), conflicts.content)

    def test_conflicts_dos_line_endings(self):
        filestore = self.make_filestore(
            [('test.txt', 'one line of content\r\n')])
        f = filestore.get_file('test.txt')
        base_rev = f.last_modified_in_revision
        # First update succeeds.
        filestore.update_file(
            'test.txt',
            'different line\r\n',
            'Test Author <test@example.com>',
            base_rev)
        # Second update with same base revision should raise an exception.
        conflicts = self.assertRaises(
            UpdateConflicts,
            filestore.update_file,
            'test.txt',
            'also change the first line\r\n',
            'Test Author <test@example.com>',
            base_rev)
        curr = filestore.get_file('test.txt')
        self.assertEqual(
            curr.last_modified_in_revision,
            conflicts.basis_rev)
        self.assertEqual(
            "<<<<<<<\r\n"
            "also change the first line\r\n"
            "=======\r\n"
            "different line\r\n"
            ">>>>>>>\r\n",
            conflicts.content)

    def test_line_endings_unix_not_normalised(self):
        # If the underlying file has unix file endings, and the post param has
        # dos endings, and match_line_endings is False, the posted content
        # will completely replace the saved file.
        filestore = self.make_filestore(
            [('test.txt', 'several\nlines\nof\ncontent')])
        f = filestore.get_file('test.txt')
        base_rev = f.last_modified_in_revision
        # Updating the text with dos endings doesn't convert the file.
        filestore.update_file(
            'test.txt',
            'several\r\nslightly different lines\r\nof\r\ncontent',
            'Test Author <test@example.com>',
            base_rev)
        curr = filestore.get_file('test.txt')
        self.assertEqual(
            'several\r\nslightly different lines\r\nof\r\ncontent',
            curr.get_content())

    def test_line_endings_unix(self):
        # If the underlying file has unix file endings, and the post param has
        # dos endings, the post param is converted before the merge is
        # attempted if match_line_endings is True.
        filestore = self.make_filestore(
            [('test.txt', 'several\nlines\nof\ncontent')])
        f = filestore.get_file('test.txt')
        base_rev = f.last_modified_in_revision
        # Updating the text with dos endings doesn't convert the file.
        filestore.update_file(
            'test.txt',
            'several\r\nslightly different lines\r\nof\r\ncontent',
            'Test Author <test@example.com>',
            base_rev, match_line_endings=True)
        curr = filestore.get_file('test.txt')
        self.assertEqual(
            'several\nslightly different lines\nof\ncontent',
            curr.get_content())

    def test_line_endings_new_file(self):
        # Line endings for new files default to '\n'.
        filestore = self.make_filestore()
        filestore.update_file(
            'new-file.txt',
            'some\r\ndos\r\nline\r\nendings',
            'Test Author <test@example.com>',
            None, match_line_endings=True)
        curr = filestore.get_file('new-file.txt')
        self.assertEqual(
            'some\ndos\nline\nendings',
            curr.get_content())
