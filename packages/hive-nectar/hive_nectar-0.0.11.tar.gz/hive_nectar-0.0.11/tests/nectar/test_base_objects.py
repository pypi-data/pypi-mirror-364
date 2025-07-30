# -*- coding: utf-8 -*-
import unittest

from nectar import Steem, exceptions
from nectar.account import Account
from nectar.instance import set_shared_steem_instance
from nectar.witness import Witness

from .nodes import get_hive_nodes


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bts = Steem(node=get_hive_nodes(), nobroadcast=True, num_retries=10)
        set_shared_steem_instance(cls.bts)

    def test_Account(self):
        with self.assertRaises(exceptions.AccountDoesNotExistsException):
            Account("FOObarNonExisting")

        c = Account("test")
        self.assertEqual(c["name"], "test")
        self.assertIsInstance(c, Account)

    def test_Witness(self):
        with self.assertRaises(exceptions.WitnessDoesNotExistsException):
            Witness("FOObarNonExisting")

        c = Witness("jesta")
        self.assertEqual(c["owner"], "jesta")
        self.assertIsInstance(c.account, Account)
