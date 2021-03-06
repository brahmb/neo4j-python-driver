#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2002-2018 "Neo4j,"
# Neo4j Sweden AB [http://neo4j.com]
#
# This file is part of Neo4j.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from neobolt.exceptions import ServiceUnavailable

from neo4j.v1 import GraphDatabase, DirectDriver

from test.stub.tools import StubTestCase, StubCluster


class DirectDriverTestCase(StubTestCase):

    def test_bolt_uri_constructs_direct_driver(self):
        with StubCluster({9001: "empty.script"}):
            uri = "bolt://127.0.0.1:9001"
            with GraphDatabase.driver(uri, auth=self.auth_token, encrypted=False) as driver:
                assert isinstance(driver, DirectDriver)

    def test_direct_disconnect_on_run(self):
        with StubCluster({9001: "disconnect_on_run.script"}):
            uri = "bolt://127.0.0.1:9001"
            with GraphDatabase.driver(uri, auth=self.auth_token, encrypted=False) as driver:
                with self.assertRaises(ServiceUnavailable):
                    with driver.session() as session:
                        session.run("RETURN $x", {"x": 1}).consume()

    def test_direct_disconnect_on_pull_all(self):
        with StubCluster({9001: "disconnect_on_pull_all.script"}):
            uri = "bolt://127.0.0.1:9001"
            with GraphDatabase.driver(uri, auth=self.auth_token, encrypted=False) as driver:
                with self.assertRaises(ServiceUnavailable):
                    with driver.session() as session:
                        session.run("RETURN $x", {"x": 1}).consume()

    def test_direct_should_reject_routing_context(self):
            uri = "bolt://127.0.0.1:9001/?name=molly&age=1"
            with self.assertRaises(ValueError):
                GraphDatabase.driver(uri, auth=self.auth_token, encrypted=False)

    def test_direct_session_close_after_server_close(self):
        with StubCluster({9001: "disconnect_after_init.script"}):
            uri = "bolt://127.0.0.1:9001"
            with GraphDatabase.driver(uri, auth=self.auth_token, encrypted=False, max_retry_time=0) as driver:
                with driver.session() as session:
                    with self.assertRaises(ServiceUnavailable):
                        session.write_transaction(lambda tx: tx.run("CREATE (a:Item)"))
