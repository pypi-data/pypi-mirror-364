# coding=utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import copy
import unittest
import uuid
from unittest import mock

from callee import Contains

from mozphab import environment, exceptions, helpers, mozphab, repository
from mozphab.commands import submit
from mozphab.commits import Commit

from .conftest import search_diff, search_rev


def reviewers_dict(reviewers=None):
    return {
        "request": reviewers[0] if reviewers else [],
        "granted": reviewers[1] if reviewers else [],
    }


def commit(
    bug_id=None, reviewers=None, body="", name="", title="", rev_id=None, wip=False
):
    return Commit(
        name=name,
        title=title,
        bug_id=bug_id,
        reviewers=reviewers_dict(reviewers),
        body=body,
        rev_id=rev_id,
        node=uuid.uuid4().hex,
        submit=True,
        wip=wip,
    )


# noinspection PyPep8Naming,PyBroadException
class Commits(unittest.TestCase):
    def _assertNoError(self, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except exceptions.Error as e:
            self.fail("%s raised" % e)

    def _assertError(self, callableObj, expected, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except exceptions.Error as e:
            if expected != str(e).strip():
                self.fail("%s not raised" % expected)
            return
        except Exception as e:
            self.fail("%s raised" % e)
        self.fail("%s failed to raise Error" % callableObj)

    @mock.patch("mozphab.conduit.ConduitAPI.check_for_invalid_reviewers")
    @mock.patch("mozphab.conduit.ConduitAPI.get_revisions")
    @mock.patch("mozphab.conduit.ConduitAPI.whoami")
    def test_commit_validation(self, m_whoami, m_get_revs, check_reviewers):
        check_reviewers.return_value = []
        repo = repository.Repository("", "", "dummy")
        check = repo.check_commits_for_submit

        self._assertNoError(check, [])
        self._assertNoError(check, [commit("1", (["r"], []))])
        self._assertNoError(
            check,
            [
                commit("1", (["r1"], [])),
                commit("2", (["r1"], [])),
                commit("3", (["r1", "r2"], [])),
            ],
        )
        self._assertNoError(check, [commit("1", None)])
        self._assertNoError(check, [commit("1", (["r"], [])), commit("1", None)])

        self._assertError(check, "- missing bug-id", [commit(None, (["r"], []))])
        self._assertNoError(check, [commit(None, (["r"], []))], require_bug=False)
        self._assertError(check, "- missing bug-id", [commit("", (["r"], []))])
        self._assertError(
            check,
            "- missing bug-id",
            [commit("1", (["r"], [])), commit("", (["r"], []))],
        )
        self._assertNoError(
            check,
            [commit("1", (["r"], [])), commit("", (["r"], []))],
            require_bug=False,
        )

        self._assertError(
            check,
            "- contains arc fields",
            [commit("1", (["r"], []), body="Summary: blah\nReviewers: r")],
        )

        m_whoami.return_value = {"phid": "PHID-1"}
        m_get_revs.return_value = [{"fields": {"authorPHID": "PHID-1"}}]
        self._assertNoError(check, [commit(bug_id=1, rev_id=1)])
        m_whoami.return_value = {"phid": "PHID-2"}
        self._assertNoError(check, [commit(bug_id=1, rev_id=1)])

    @mock.patch("mozphab.conduit.ConduitAPI.check_for_invalid_reviewers")
    def test_invalid_reviewers_fails_the_stack_validation_check(self, check_reviewers):
        class Args:
            def __init__(self):
                self.force = False

        def fail_gonzo(reviewers):
            # Replace the check_for_invalid_reviewers() function with something that
            # fails if "gonzo" is in the reviewers list.
            if "gonzo" in reviewers["request"]:
                return [{"name": "gonzo"}]
            elif "goober" in reviewers["request"]:
                return [{"name": "goober", "until": "string"}]
            else:
                return []

        check_reviewers.side_effect = fail_gonzo
        repo = repository.Repository("", "", "dummy")
        repo.args = Args()

        self._assertError(
            repo.check_commits_for_submit,
            "- gonzo is not a valid reviewer's name",
            (
                # Build a stack with an invalid reviewer in the middle.
                [
                    commit("1", (["alice"], [])),
                    commit("2", (["bob", "gonzo"], [])),
                    commit("3", (["charlie"], [])),
                ]
            ),
        )

        self._assertError(
            repo.check_commits_for_submit,
            "- goober is not available until string (submit anyway with `-f`)",
            (
                # Build a stack with an unavailable reviewer in the middle.
                [
                    commit("1", (["alice"], [])),
                    commit("2", (["bob", "goober"], [])),
                    commit("3", (["charlie"], [])),
                ]
            ),
        )

        repo.args.force = True
        self._assertNoError(
            repo.check_commits_for_submit,
            (
                [
                    commit("1", (["alice"], [])),
                    commit("2", (["bob", "goober"], [])),
                    commit("3", (["charlie"], [])),
                ]
            ),
        )

    @mock.patch("mozphab.mozphab.conduit.get_revisions")
    @mock.patch("mozphab.conduit.ConduitAPI.check_for_invalid_reviewers")
    def test_validate_duplicate_revision(self, check_reviewers, get_revisions):
        check_reviewers.return_value = []
        get_revisions.return_value = [True]

        repo = repository.Repository("", "", "dummy")

        self._assertNoError(
            repo.check_commits_for_submit,
            (
                [
                    commit("1", (["r"], []), name="a"),
                    commit("2", (["r"], []), name="b"),
                    commit("3", (["r"], []), name="c"),
                ]
            ),
        )

        self._assertNoError(
            repo.check_commits_for_submit,
            (
                [
                    commit("1", (["r"], []), rev_id="1", name="a"),
                    commit("2", (["r"], []), rev_id="2", name="b"),
                    commit("3", (["r"], []), rev_id="3", name="c"),
                ]
            ),
        )

        self._assertError(
            repo.check_commits_for_submit,
            "Phabricator revisions should be unique, "
            "but the following commits refer to the same one (D1):\n"
            "* a\n"
            "* c",
            (
                [
                    commit("1", (["r"], []), rev_id="1", name="a"),
                    commit("2", (["r"], []), rev_id="2", name="b"),
                    commit("3", (["r"], []), rev_id="1", name="c"),
                ]
            ),
        )

        self._assertError(
            repo.check_commits_for_submit,
            "Phabricator revisions should be unique, "
            "but the following commits refer to the same one (D1):\n"
            "* a\n"
            "* c"
            "\n\n\n"
            "Phabricator revisions should be unique, "
            "but the following commits refer to the same one (D2):\n"
            "* b\n"
            "* d",
            (
                [
                    commit("1", (["r"], []), rev_id="1", name="a"),
                    commit("2", (["r"], []), rev_id="2", name="b"),
                    commit("3", (["r"], []), rev_id="1", name="c"),
                    commit("4", (["r"], []), rev_id="2", name="d"),
                ]
            ),
        )

    def test_commit_preview(self):
        build = helpers.build_commit_title

        self.assertEqual(
            "Bug 1, blah, r=turnip",
            build(commit("1", ([], ["turnip"]), title="bug 1, blah, r=turnip")),
        )
        self.assertEqual(
            "blah (Bug 1) r=turnip",
            build(commit("1", ([], ["turnip"]), title="blah (bug 1) r=turnip")),
        )
        self.assertEqual(
            "Bug 1 - blah r?turnip",
            build(commit("1", (["turnip"], []), title="blah r?turnip")),
        )

        self.assertEqual(
            "blah r=turnip", build(commit("", ([], ["turnip"]), title="blah r=turnip"))
        )
        self.assertEqual(
            "Bug 1 - blah", build(commit("1", None, title="Bug 1 - blah r?turnip"))
        )
        self.assertEqual(
            "Bug 1 - blah", build(commit("1", None, title="Bug 1 - blah r=turnip"))
        )
        self.assertEqual(
            "Bug 1 - helper_bug2.html",
            build(commit("1", None, title="Bug 1 - helper_bug2.html")),
        )

    @mock.patch("mozphab.helpers.build_commit_title")
    def test_update_commit_title_previews(self, m_build_commit_title):
        m_build_commit_title.side_effect = lambda x: x.title + " preview"
        commits = [Commit(title="a"), Commit(title="b")]
        helpers.update_commit_title_previews(commits)
        self.assertEqual(
            [
                Commit(title="a", title_preview="a preview"),
                Commit(title="b", title_preview="b preview"),
            ],
            commits,
        )

    def test_replace_request_reviewers(self):
        replace = helpers.replace_reviewers
        self.assertEqual("", replace("", reviewers_dict()))
        self.assertEqual("Title", replace("Title", reviewers_dict()))
        self.assertEqual(
            "Title\n\nr?one r=two", replace("Title\n\nr?one r=two", reviewers_dict())
        )
        self.assertEqual("r?one", replace("", reviewers_dict([["one"], []])))
        self.assertEqual("r?one", replace("r?one", reviewers_dict([["one"], []])))
        self.assertEqual("r?one,two", replace("", reviewers_dict([["one", "two"], []])))
        self.assertEqual(
            "Some Title r?one,two",
            replace("Some Title", reviewers_dict([["one", "two"], []])),
        )
        self.assertEqual(
            "Title r?one\n\nDescr\niption",
            replace("Title\n\nDescr\niption", reviewers_dict([["one"], []])),
        )
        self.assertEqual(
            "Title r?one,two\n\nr?two",
            replace("Title\n\nr?two", reviewers_dict([["one", "two"], []])),
        )

        self.assertEqual("Title", replace("Title r?one", reviewers_dict()))
        self.assertEqual("Title", replace("Title r?one,two", reviewers_dict()))
        self.assertEqual("Title", replace("Title r?one r?two", reviewers_dict()))
        self.assertEqual(
            "Title r?one!", replace("Title r?one!", reviewers_dict([["one!"], []]))
        )
        self.assertEqual(
            "Title r?one", replace("Title r?one!", reviewers_dict([["one"], []]))
        )
        self.assertEqual(
            "Title r?one!", replace("Title r?one", reviewers_dict([["one!"], []]))
        )
        self.assertEqual(
            "Title r?one", replace("Title r?one", reviewers_dict([["one"], []]))
        )
        self.assertEqual(
            "Title r?one one", replace("Title r? one", reviewers_dict([["one"], []]))
        )
        self.assertEqual(
            "Title r?one,two",
            replace("Title r?one,two", reviewers_dict([["one", "two"], []])),
        )
        self.assertEqual(
            "Title r?one,two",
            replace("Title r?two", reviewers_dict([["one", "two"], []])),
        )
        self.assertEqual(
            "Title r?one,two",
            replace("Title r?one r?two", reviewers_dict([["one", "two"], []])),
        )
        self.assertEqual(
            "Title r?one", replace("Title r=one", reviewers_dict([["one"], []]))
        )
        self.assertEqual(
            "Title r?one", replace("Title r=one,two", reviewers_dict([["one"], []]))
        )
        self.assertEqual(
            "Title r?one,two",
            replace("Title r=one,two", reviewers_dict([["one", "two"], []])),
        )
        self.assertEqual(
            "Title r?one,two",
            replace("Title r=one r=two", reviewers_dict([["one", "two"], []])),
        )
        self.assertEqual(
            "Title r?one,two",
            replace("Title r?one r=two", reviewers_dict([["one", "two"], []])),
        )

    def test_replace_granted_reviewers(self):
        replace = helpers.replace_reviewers
        self.assertEqual("r=one", replace("", reviewers_dict([[], ["one"]])))
        self.assertEqual("r=one", replace("r=one", reviewers_dict([[], ["one"]])))
        self.assertEqual("r=one,two", replace("", reviewers_dict([[], ["one", "two"]])))
        self.assertEqual(
            "Some Title r=one,two",
            replace("Some Title", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual(
            "Title r=one\n\nDescr\niption",
            replace("Title\n\nDescr\niption", reviewers_dict([[], ["one"]])),
        )
        self.assertEqual(
            "Title r=one,two\n\nr?two",
            replace("Title\n\nr?two", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual("Title", replace("Title r=one", reviewers_dict()))
        self.assertEqual("Title", replace("Title r=one,two", reviewers_dict()))
        self.assertEqual("Title", replace("Title r=one r=two", reviewers_dict()))
        self.assertEqual(
            "Title r=one", replace("Title r=one", reviewers_dict([[], ["one"]]))
        )
        self.assertEqual(
            "Title r=one!", replace("Title r=one!", reviewers_dict([[], ["one!"]]))
        )
        self.assertEqual(
            "Title r=one", replace("Title r=one!", reviewers_dict([[], ["one"]]))
        )
        self.assertEqual(
            "Title r=one!", replace("Title r=one", reviewers_dict([[], ["one!"]]))
        )
        self.assertEqual(
            "Title r=one one", replace("Title r= one", reviewers_dict([[], ["one"]]))
        )
        self.assertEqual(
            "Title r=one,two",
            replace("Title r=one,two", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual(
            "Title r=one,two",
            replace("Title r=two", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual(
            "Title r=one,two",
            replace("Title r=one r=two", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual(
            "Title r=one", replace("Title r?one", reviewers_dict([[], ["one"]]))
        )
        self.assertEqual(
            "Title r=one", replace("Title r?one,two", reviewers_dict([[], ["one"]]))
        )
        self.assertEqual(
            "Title r=one,two",
            replace("Title r?one,two", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual(
            "Title r=one,two",
            replace("Title r?one r?two", reviewers_dict([[], ["one", "two"]])),
        )
        self.assertEqual(
            "Title r=one,two",
            replace("Title r=one r?two", reviewers_dict([[], ["one", "two"]])),
        )

    def test_replace_mixed_reviewers(self):
        replace = helpers.replace_reviewers
        self.assertEqual(
            "Title r?one r=two", replace("Title", reviewers_dict([["one"], ["two"]]))
        )
        self.assertEqual(
            "Title r?one r=two",
            replace("Title r=one r?two", reviewers_dict([["one"], ["two"]])),
        )
        self.assertEqual(
            "Title r?one r=two",
            replace("Title r?two r=one", reviewers_dict([["one"], ["two"]])),
        )
        self.assertEqual(
            "Title r?one,two r=three",
            replace("Title r=one r?two", reviewers_dict([["one", "two"], ["three"]])),
        )
        self.assertEqual(
            "Title r?one r=two,three",
            replace("Title r=one r?two", reviewers_dict([["one"], ["two", "three"]])),
        )

    @unittest.skip("These tests should pass we should fix the function")
    def test_badly_replaced_reviewers(self):
        replace = mozphab.replace_reviewers
        # r?two
        self.assertEqual("r?one", replace("r?two", reviewers_dict([["one"], []])))
        # r=one
        self.assertEqual("r?one", replace("r=one", reviewers_dict([["one"], []])))
        # r? one
        self.assertEqual("r?one one", replace("r? one", reviewers_dict([["one"], []])))
        # r?one,
        self.assertEqual("r?one", replace("r?one,", reviewers_dict([["one"], []])))
        # r?one
        self.assertEqual(
            "r?one,two", replace("r?one", reviewers_dict([["one", "two"], []]))
        )
        # r?one,two
        self.assertEqual("r?one", replace("r?one,two", reviewers_dict([["one"], []])))
        # Title r?one,two,,two
        self.assertEqual(
            "Title r?one,two",
            replace("Title r?one,,two", reviewers_dict([["one"], ["two"], []])),
        )
        # r?one
        self.assertEqual("", replace("r?one", reviewers_dict()))
        # r?one,two
        self.assertEqual("", replace("r?one,two", reviewers_dict()))
        # r?one
        self.assertEqual("", replace("r?one r?two", reviewers_dict()))
        # r?two
        self.assertEqual(
            "r?one,two", replace("r?two", reviewers_dict([["one", "two"], []]))
        )
        # r?one r?one,two
        self.assertEqual(
            "r?one,two", replace("r?one r?two", reviewers_dict([["one", "two"], []]))
        )
        # r=one
        self.assertEqual("r?one", replace("r=one", reviewers_dict([["one"], []])))
        # r=one,two
        self.assertEqual("r?one", replace("r=one,two", reviewers_dict([["one"], []])))
        # r=one,two
        self.assertEqual(
            "r?one,two", replace("r=one,two", reviewers_dict([["one", "two"], []]))
        )
        # r=one, r?one,two
        self.assertEqual(
            "r?one,two", replace("r=one r=two", reviewers_dict([["one", "two"], []]))
        )
        # r? one, r?one,two
        self.assertEqual(
            "r?one,two", replace("r?one r=two", reviewers_dict([["one", "two"], []]))
        )

        # Granted
        # r=two
        self.assertEqual("r=one", replace("r=two", reviewers_dict([[], ["one"]])))
        # r?one
        self.assertEqual("r=one", replace("r?one", reviewers_dict([[], ["one"]])))
        # r?one
        self.assertEqual(
            "r=one,two", replace("r=one", reviewers_dict([[], ["one", "two"]]))
        )
        # r?one,two
        self.assertEqual("r?one", replace("r?one,two", reviewers_dict([["one"], []])))

    @mock.patch("mozphab.commands.submit.conduit.get_revisions")
    @mock.patch("mozphab.commands.submit.conduit.get_diffs")
    @mock.patch("mozphab.commands.submit.conduit.whoami")
    @mock.patch("mozphab.commands.submit.logger")
    def test_show_commit_stack(
        self, mock_logger, m_whoami, m_get_diffs, m_get_revisions
    ):
        class Repository:
            phab_url = "http://phab"
            path = "x"
            api_url = "x"
            dot_path = "x"

        class Args:
            command = "submit"
            force = False
            wip = False

        def _commit(
            name="aaa000",
            node="aaa000aaa000",
            title="A",
            rev=None,
            bug="1",
            bug_orig="1",
            granted=None,
            request=None,
            wip=False,
        ):
            granted = granted or []
            request = request or []
            return Commit(
                name=name,
                node=node,
                submit=True,
                title_preview=title,
                rev_id=rev,
                bug_id_orig=bug_orig,
                bug_id=bug,
                reviewers={"granted": granted, "request": request},
                wip=wip,
            )

        repo = Repository()
        submit.conduit.set_repo(repo)

        args = Args()

        m_whoami.return_value = {"phid": "PHID-USER-1"}
        m_get_revisions.return_value = [search_rev()]
        m_get_diffs.return_value = {"PHID-DIFF-1": search_diff()}

        submit.show_commit_stack([], args)
        self.assertFalse(mock_logger.info.called, "logger.info() shouldn't be called")
        self.assertFalse(
            mock_logger.warning.called, "logger.warning() shouldn't be called"
        )

        submit.show_commit_stack(
            [Commit(name="aaa000", title_preview="A")], args, validate=False
        )
        mock_logger.info.assert_called_with("%s %s %s", "(New)", "aaa000", "A")
        self.assertFalse(
            mock_logger.warning.called, "logger.warning() shouldn't be called"
        )
        mock_logger.reset_mock()

        submit.show_commit_stack([_commit(rev=12)], args, validate=False)
        mock_logger.info.assert_called_with("%s %s %s", "(D12)", "aaa000", "A")
        self.assertFalse(
            mock_logger.warning.called, "logger.warning() shouldn't be called"
        )
        mock_logger.reset_mock()

        submit.show_commit_stack(
            [_commit(), _commit(name="bbb000", title="B")],
            args,
            validate=False,
        )
        self.assertEqual(2, mock_logger.info.call_count)
        self.assertEqual(
            [
                mock.call("%s %s %s", "(New)", "bbb000", "B"),
                mock.call("%s %s %s", "(New)", "aaa000", "A"),
            ],
            mock_logger.info.call_args_list,
        )
        mock_logger.reset_mock()

        submit.show_commit_stack(
            [_commit(bug_orig=2, bug=1, granted=["alice"])], args, validate=True
        )
        mock_logger.info.assert_called_with("%s %s %s", "(New)", "aaa000", "A")
        mock_logger.warning.assert_called_with("!! Bug ID changed from %s to %s", 2, 1)

        # Submit with missing bug ID.
        mock_logger.reset_mock()
        submit.show_commit_stack(
            [_commit(bug="", bug_orig="", request=["bob"])], args, validate=True
        )
        mock_logger.warning.assert_called_with(Contains("Missing Bug ID"))

        # Submit with missing reviewers.
        mock_logger.reset_mock()
        submit.show_commit_stack([_commit()], args, validate=True)
        mock_logger.warning.assert_called_with(Contains("Missing reviewers"))

        # Submit with existing revision reviewers.
        mock_logger.reset_mock()
        m_get_revisions.return_value = [search_rev(reviewers=["PHID-USER-2"])]
        submit.show_commit_stack([_commit(rev=1)], args, validate=True)
        mock_logger.warning.assert_not_called()

        mock_logger.reset_mock()
        submit.show_commit_stack(
            [_commit(rev=123)],
            args,
            validate=False,
            show_rev_urls=True,
        )
        mock_logger.warning.assert_called_with("-> %s/D%s", "http://phab", 123)

        # Do not update not changed commits
        mock_logger.reset_mock()
        m_get_revisions.return_value = [
            search_rev(),
            search_rev(rev=2, phid="PHID-REV-2", diff="PHID-DIFF-2"),
        ]
        m_get_diffs.return_value = {
            "PHID-DIFF-1": search_diff(),
            "PHID-DIFF-2": search_diff(),
        }
        # we're changing bug id in the first revision to 2
        submit.show_commit_stack(
            [
                _commit(rev=1, bug="2", bug_orig="2", granted=["alice"]),
                _commit(
                    name="bbb000",
                    node="bbb000bbb000",
                    title="B",
                    rev=2,
                    granted=["alice"],
                ),
            ],
            args,
            validate=True,
        )
        mock_logger.warning.assert_called_once_with(
            "!! Bug ID in Phabricator revision will change from %s to %s", "1", "2"
        )

        mock_logger.reset_mock()
        m_whoami.return_value = {"phid": "PHID-USER-2"}
        submit.show_commit_stack(
            [_commit(rev=1, granted=["alice"])],
            args,
            validate=True,
        )
        mock_logger.warning.assert_called_once_with(Contains("Commandeer"))

        # Information about not updating the commit if not changed
        mock_logger.reset_mock()
        m_whoami.return_value = {"phid": "PHID-USER-1"}
        m_get_revisions.return_value = [search_rev(reviewers=["PHID-USER-2"])]
        m_get_diffs.return_value = {"PHID-DIFF-1": search_diff()}

        submit.show_commit_stack(
            [_commit(rev=1, granted=["alice"])], args, validate=True
        )
        assert mock_logger.info.call_args_list[1] == mock.call(
            Contains("revision has not changed")
        )

        # Removing the WIP state from the revision without changing the commit's SHA1
        mock_logger.reset_mock()
        m_get_revisions.return_value = [search_rev(status="changes-planned")]
        submit.show_commit_stack(
            [_commit(rev=1, granted=["alice"])], args, validate=True
        )
        mock_logger.warning.assert_called_once_with(
            Contains('"Changes Planned" status will change')
        )

        # Adding the WIP state to the revision without changing the commit's SHA1
        mock_logger.reset_mock()
        args.wip = True
        m_get_revisions.return_value = [search_rev()]
        submit.show_commit_stack(
            [_commit(rev=1, granted=["alice"], wip=True)], args, validate=True
        )
        mock_logger.warning.assert_called_with(
            Contains('status will change to "Changes Planned"')
        )

        # Submit a new patch without reviewers.
        mock_logger.reset_mock()
        args.wip = False
        submit.show_commit_stack(
            [_commit(rev=None, request=[], wip=True)], args, validate=True
        )
        mock_logger.warning.assert_any_call(Contains("Missing reviewers"))
        mock_logger.warning.assert_any_call(Contains('submitted as "Changes Planned"'))

        # Submit a new WIP patch with reviewers.
        mock_logger.reset_mock()
        args.wip = True
        submit.show_commit_stack(
            [_commit(rev=None, request=["alice"], wip=True)], args, validate=True
        )
        mock_logger.warning.assert_not_called()

        # Submit a new patch with the WIP prefix.
        mock_logger.reset_mock()
        args.wip = False
        submit.show_commit_stack(
            [_commit(title="WIP: A", request=["alice"], wip=True)], args, validate=True
        )
        mock_logger.warning.assert_called_with(
            Contains('submitted as "Changes Planned"')
        )

        # Submitting a stack of two commits with one revision already on Phabricator
        # should properly set `commit.rev_phid` with `validate=True`.
        mock_logger.reset_mock()
        commits = [_commit(title="submitted", rev=1), _commit(title="new", rev=None)]
        submit.show_commit_stack(
            commits,
            args,
            validate=True,
        )
        for commit in commits:
            if commit.title_preview == "submitted":
                assert (
                    commit.rev_phid == "PHID-DREV-1"
                ), "`rev_id` should be set for already submitted commit."
            elif commit.title_preview == "new":
                assert (
                    commit.rev_phid is None
                ), "`rev_id` should not be set for newly created commit."

        # Submitting a new uplift clears reviewers and shouldn't warn.
        mock_logger.reset_mock()
        args.command = "uplift"
        submit.show_commit_stack(
            [_commit(rev=None, granted=[], wip=False)], args, validate=True
        )
        mock_logger.warning.assert_not_called()

    def test_update_commits_from_args(self):
        def lwr(revs):
            return [r.lower() for r in revs]

        update = submit.update_commits_from_args

        class Args:
            def __init__(
                self,
                reviewer=None,
                blocker=None,
                bug=None,
                wip=False,
                no_wip=False,
                command="submit",
            ):
                self.reviewer = reviewer
                self.blocker = blocker
                self.bug = bug
                self.wip = wip
                self.no_wip = no_wip
                self.command = command

        _commits = [
            Commit(title="A", reviewers={"granted": [], "request": []}, bug_id=None),
            Commit(
                title="B",
                reviewers={"granted": [], "request": ["one"]},
                bug_id="1",
            ),
        ]

        # No change if noreviewer  args provided
        commits = copy.deepcopy(_commits)
        commits[1].reviewers["granted"].append("two")
        with mock.patch("mozphab.commands.submit.config") as m_config:
            m_config.always_blocking = False
            update(commits, Args())
            self.assertEqual(
                commits,
                [
                    Commit(
                        title="A",
                        reviewers={"granted": [], "request": []},
                        bug_id=None,
                        wip=True,
                    ),
                    Commit(
                        title="B",
                        reviewers={"granted": ["two"], "request": ["one"]},
                        bug_id="1",
                        wip=False,
                    ),
                ],
            )

        # Adding and removing reviewers, forcing the bug ID
        commits = copy.deepcopy(_commits)
        update(commits, Args(reviewer=["two", "three"], bug="2"))
        assert commits[0].title == "A"
        assert commits[0].bug_id == "2"
        assert "two" in commits[0].reviewers["granted"]
        assert "three" in commits[0].reviewers["granted"]

        assert commits[1].title == "B"
        assert commits[1].bug_id == "2"
        assert "two" in commits[1].reviewers["granted"]
        assert "three" in commits[1].reviewers["granted"]

        # Removing duplicates
        commits = copy.deepcopy(_commits)
        update(
            commits,
            Args(
                reviewer=["Two", "two", "two!", "three", "Three", "THREE!"],
                blocker=["Two", "THREE!", "three", "two", "three"],
            ),
        )
        assert commits[0].title == "A"
        assert commits[0].bug_id is None
        assert "two!" in lwr(commits[0].reviewers["granted"])
        assert "three!" in lwr(commits[0].reviewers["granted"])

        assert commits[1].title == "B"
        assert commits[1].bug_id == "1"
        assert "two!" in lwr(commits[1].reviewers["granted"])
        assert "three!" in lwr(commits[1].reviewers["granted"])

        # Adding blocking reviewers via args
        commits = copy.deepcopy(_commits)
        commits[1].reviewers["request"].append("three")
        commits[1].reviewers["granted"].append("four")
        commits[1].reviewers["granted"].append("five")
        update(
            commits,
            Args(
                reviewer=["one", "two!", "four"],
                blocker=["three", "four!"],
            ),
        )
        assert commits[0].title == "A"
        assert commits[0].bug_id is None
        assert "one" in lwr(commits[0].reviewers["granted"])
        assert "two!" in lwr(commits[0].reviewers["granted"])
        assert "three!" in lwr(commits[0].reviewers["granted"])
        assert "four!" in lwr(commits[0].reviewers["granted"])

        assert commits[1].title == "B"
        assert commits[1].bug_id == "1"
        assert "four!" in commits[1].reviewers["granted"]
        assert "two!" in commits[1].reviewers["granted"]
        assert "one" in commits[1].reviewers["request"]
        assert "three!" in commits[1].reviewers["request"]

        # reviewerless should result in WIP commits
        commits = copy.deepcopy(_commits)
        commits.append(Commit(title="Bug 2 - A", bug_id="2", rev_id=2))
        with mock.patch("mozphab.commands.submit.conduit.has_revision_reviewers") as m:
            m.side_effect = [
                False,  # First commit doesn't have reviewers.
                # Function isn't called for second commit since it has reviewers.
                True,  # For revision ID 2.
            ]
            update(commits, Args())
        assert commits[0].wip
        assert not commits[1].wip
        assert not commits[2].wip

        # Force WIP
        commits = copy.deepcopy(_commits)
        update(commits, Args(wip=True))
        assert commits[0].wip
        assert commits[1].wip

        # reviewerless with --no-wip shouldn't be WIP
        commits = copy.deepcopy(_commits)
        commits.append(Commit(title="WIP: Bug 2 - A", bug_id="2", wip=True))
        update(commits, Args(no_wip=True))
        assert not commits[0].wip
        assert not commits[1].wip
        assert not commits[2].wip

        # Forcing blocking reviewers
        commits = copy.deepcopy(_commits)
        commits[1].reviewers["granted"].append("two")
        with mock.patch("mozphab.commands.submit.config") as m_config:
            m_config.always_blocking = True
            update(commits, Args())
            self.assertEqual(
                commits,
                [
                    Commit(
                        title="A",
                        reviewers={"granted": [], "request": []},
                        bug_id=None,
                        wip=True,
                    ),
                    Commit(
                        title="B",
                        reviewers={"granted": ["two!"], "request": ["one!"]},
                        bug_id="1",
                        wip=False,
                    ),
                ],
            )

    def test_single_fails_with_end_rev(self):
        # --single is working with one SHA1 provided only
        repo = repository.Repository("", "", "dummy")

        class Args:
            def __init__(self, end_rev=environment.DEFAULT_END_REV):
                self.single = True
                self.end_rev = end_rev

        self._assertNoError(repo.set_args, Args())
        self._assertError(
            repo.set_args,
            "Option --single can be used with only one identifier.",
            Args("endrev"),
        )


class TestUpdateCommitSummary(unittest.TestCase):
    def test_update_revision_description(self):
        c = commit(
            rev_id="D123",
            title="hi!",
            body="hello!  µ-benchmarks are a thing.\n\n"
            "Differential Revision: http://phabricator.test/D123",
        )
        r = {"fields": {"title": "", "summary": ""}}
        t = []

        expected = [
            {"type": "title", "value": "hi!"},
            {"type": "summary", "value": "hello!  µ-benchmarks are a thing."},
        ]
        submit.update_revision_description(t, c, r)

        self.assertListEqual(t, expected)

    def test_update_revision_description_no_op(self):
        c = commit(
            rev_id="D123",
            title="hi!",
            body="hello!\n\nDifferential Revision: http://phabricator.test/D123",
        )
        r = {"fields": {"title": "hi!", "summary": "hello!\n\n"}}
        t = []

        expected = []
        submit.update_revision_description(t, c, r)

        self.assertListEqual(t, expected)

    @mock.patch("mozphab.conduit.ConduitAPI.get_users")
    def test_update_revision_reviewers(self, m_get_users):
        # From https://phabricator.services.mozilla.com/api/differential.revision.edit
        #
        # Example call format we are aiming for:
        #
        # $ echo '{
        #   "transactions": [
        #     {
        #       "type": "reviewers.set",
        #       "value": ["PHID-USER-1", "blocking(PHID-USER-2)"]
        #     }
        #   ],
        #   "objectIdentifier": "D8095"
        # }' | arc call-conduit --conduit-uri \
        #       https://phabricator.services.mozilla.com/ \
        #       --conduit-token <conduit-token> differential.revision.edit
        m_get_users.side_effect = (
            [
                {"phid": "PHID-USER-1"},
                {"phid": "PHID-USER-2"},
                {"phid": "PHID-USER-3"},
            ],
            [{"phid": "PHID-USER-1"}],
            [{"phid": "PHID-USER-2"}, {"phid": "PHID-USER-3"}],
        )
        c = commit(rev_id="123", reviewers=[["alice", "bob!"], ["frankie!"]])
        t = []

        expected = [
            {
                "type": "reviewers.set",
                "value": [
                    "PHID-USER-1",
                    "blocking(PHID-USER-2)",
                    "blocking(PHID-USER-3)",
                ],
            }
        ]
        mozphab.conduit.update_revision_reviewers(t, c)

        self.assertEqual(
            m_get_users.call_args_list,
            [
                mock.call(["alice", "bob!", "frankie!"]),
                mock.call(["alice"]),
                mock.call(["bob", "frankie"]),
            ],
        )
        self.assertListEqual(t, expected)

    def test_parse_api_response_with_no_problems(self):
        # Response comes from running:
        # $ echo '{... (some valid update summary JSON) ...}' | \
        #   arc call-conduit differential.revision.edit
        api_response = (
            '{"error":null,"errorMessage":null,"response":{"object":{'
            '"id":56,"phid":"PHID-DREV-ke6jhbdnwd5chtnk2q5w"},'
            '"transactions":[{"phid":"PHID-XACT-DREV-itlxgx7rsjrcnta"}]}} '
        )
        self.assertEqual(None, helpers.parse_api_error(api_response))

    def test_parse_api_response_with_errors(self):
        # Error response from running:
        # $ echo '{}' | arc call-conduit differential.revision.edit
        api_response = (
            '{"error":"ERR-CONDUIT-CORE", '
            '"errorMessage":"ERR-CONDUIT-CORE: Parameter '
            '\\"transactions\\" is not a list of transactions.",'
            '"response":null} '
        )
        self.assertEqual(
            'ERR-CONDUIT-CORE: Parameter "transactions" is not a list of transactions.',
            helpers.parse_api_error(api_response),
        )

    def test_update_revision_no_bug_id(self):
        # Phabricator stores patches with no bug as having an empty string as the
        # bug ID. We should not explicitly update the bug-id if our bug id is "None".
        transactions = []
        submit.update_revision_bug_id(
            transactions, Commit(bug_id=None), {"fields": {"bugzilla.bug-id": ""}}
        )
        self.assertEqual([], transactions)


if __name__ == "__main__":
    unittest.main()
